"""
Physics and Mathematical Telemetry Generation Engine.
Implements realistic voltage oscillations, solar diurnal battery cycles, and RF signal drift.
"""

from datetime import datetime, timezone, timedelta
import math
import random
from typing import Dict, List, Optional

from config_loader import AppConfig, VoltageProfile
from engine.models import DeviceOperationalState, SimulatedDeviceState, TelemetryReadingPayload


class TelemetryGenerator:
    def __init__(self, config: AppConfig):
        self.config = config
        self.profiles: Dict[str, VoltageProfile] = config.voltage_profiles
        self.devices: Dict[str, SimulatedDeviceState] = {}
        self._initialize_device_states()

    def _initialize_device_states(self) -> None:
        """Initializes runtime tracking states for all configured gateways and fences."""
        for gw in self.config.gateways:
            for fence in gw.fences:
                for dev in fence.devices:
                    state = DeviceOperationalState.from_str(dev.initial_state)
                    self.devices[dev.serial] = SimulatedDeviceState(
                        serial=dev.serial,
                        section_code=dev.section_code,
                        section_name=dev.section_name,
                        fence_code=fence.code,
                        fence_name=fence.name,
                        gateway_id=gw.id,
                        nominal_voltage=dev.nominal_voltage,
                        current_state=state,
                        battery_level=random.uniform(90.0, 98.0),
                        signal_strength=random.uniform(80.0, 95.0),
                    )

    def set_device_state(
        self,
        serial: str,
        state: DeviceOperationalState,
        duration_seconds: Optional[float] = None,
    ) -> bool:
        """Dynamically sets a fault or operational state on a specific device."""
        if serial not in self.devices:
            return False
        dev = self.devices[serial]
        dev.current_state = state
        dev.state_start_time = datetime.now(timezone.utc)
        dev.state_duration_seconds = duration_seconds
        return True

    def set_fence_state(
        self,
        fence_code: str,
        state: DeviceOperationalState,
        duration_seconds: Optional[float] = None,
    ) -> int:
        """Sets operational state across all devices on a given fence."""
        count = 0
        for dev in self.devices.values():
            if dev.fence_code.upper() == fence_code.upper():
                dev.current_state = state
                dev.state_start_time = datetime.now(timezone.utc)
                dev.state_duration_seconds = duration_seconds
                count += 1
        return count

    def reset_all_to_normal(self) -> None:
        """Restores all devices to healthy normal operating state."""
        for dev in self.devices.values():
            dev.current_state = DeviceOperationalState.NORMAL
            dev.state_duration_seconds = None

    def generate_reading_for_device(
        self,
        dev: SimulatedDeviceState,
        target_time: Optional[datetime] = None,
    ) -> Optional[TelemetryReadingPayload]:
        """
        Generates a realistic telemetry reading for a single device at a given timestamp.
        Returns None if device is simulated as OFFLINE.
        """
        if target_time is None:
            target_time = datetime.now(timezone.utc)

        # 1. Check if temporary state duration has expired
        if dev.state_duration_seconds is not None:
            elapsed = (target_time - dev.state_start_time).total_seconds()
            if elapsed > dev.state_duration_seconds:
                dev.current_state = DeviceOperationalState.NORMAL
                dev.state_duration_seconds = None

        # 2. Check offline state
        if dev.current_state == DeviceOperationalState.OFFLINE:
            return None

        # 3. Calculate Realistic Voltage (kV)
        voltage = self._calculate_voltage(dev)

        # 4. Calculate Battery Level (%) with Solar Diurnal Cycle
        battery = self._calculate_battery(dev, target_time)

        # 5. Calculate Cellular / LoRa Signal (%)
        signal = self._calculate_signal(dev)

        reading = TelemetryReadingPayload(
            deviceSerial=dev.serial,
            voltage=voltage,
            battery=battery,
            signal=signal,
            timestamp=target_time,
        )
        dev.last_reading = reading
        return reading

    def generate_readings_for_gateway(
        self,
        gateway_id: str,
        target_time: Optional[datetime] = None,
    ) -> List[TelemetryReadingPayload]:
        """Generates telemetry readings for all devices connected to a specific gateway."""
        readings = []
        for dev in self.devices.values():
            if dev.gateway_id.upper() == gateway_id.upper():
                r = self.generate_reading_for_device(dev, target_time)
                if r is not None:
                    readings.append(r)
        return readings

    def generate_all_readings(
        self,
        target_time: Optional[datetime] = None,
    ) -> List[TelemetryReadingPayload]:
        """Generates current telemetry readings for all online devices."""
        readings = []
        for dev in self.devices.values():
            r = self.generate_reading_for_device(dev, target_time)
            if r is not None:
                readings.append(r)
        return readings

    def _calculate_voltage(self, dev: SimulatedDeviceState) -> float:
        """Calculates voltage based on operational state and Gaussian electrical noise."""
        profile_key = dev.current_state.value
        profile = self.profiles.get(profile_key)

        if dev.current_state == DeviceOperationalState.NORMAL:
            nominal = dev.nominal_voltage
            noise_std = profile.noise_std if profile else 0.15
            min_kv = profile.min_kv if profile else 5.5
            max_kv = profile.max_kv if profile else 8.5
            noise = random.gauss(0, noise_std) if self.config.simulation.enable_jitter else 0.0
            return max(min_kv, min(max_kv, nominal + noise))

        elif dev.current_state == DeviceOperationalState.VEGETATION_WARNING:
            nominal = profile.nominal_kv if profile else 4.0
            noise_std = profile.noise_std if profile else 0.25
            min_kv = profile.min_kv if profile else 3.0
            max_kv = profile.max_kv if profile else 4.8
            noise = random.gauss(0, noise_std) if self.config.simulation.enable_jitter else 0.0
            return max(min_kv, min(max_kv, nominal + noise))

        elif dev.current_state == DeviceOperationalState.CRITICAL_BREACH:
            nominal = profile.nominal_kv if profile else 0.2
            noise_std = profile.noise_std if profile else 0.08
            min_kv = profile.min_kv if profile else 0.0
            max_kv = profile.max_kv if profile else 1.2
            noise = abs(random.gauss(0, noise_std)) if self.config.simulation.enable_jitter else 0.0
            return max(min_kv, min(max_kv, nominal + noise))

        elif dev.current_state == DeviceOperationalState.LOW_BATTERY:
            # Low battery may slightly degrade energizer output
            nominal = dev.nominal_voltage * 0.85
            noise = random.gauss(0, 0.2) if self.config.simulation.enable_jitter else 0.0
            return max(4.5, min(7.5, nominal + noise))

        return dev.nominal_voltage

    def _calculate_battery(self, dev: SimulatedDeviceState, target_time: datetime) -> int:
        """Simulates battery level using a 24-hour solar diurnal charging/discharging model."""
        if dev.current_state == DeviceOperationalState.LOW_BATTERY:
            # Low battery fault preset
            dev.battery_level = max(5.0, min(14.0, dev.battery_level - random.uniform(0.1, 0.5)))
            return int(round(dev.battery_level))

        if not self.config.simulation.simulate_solar_battery:
            return int(round(dev.battery_level))

        # Solar hour (0.0 to 24.0 in local time)
        hour = target_time.hour + target_time.minute / 60.0

        if 6.0 <= hour <= 18.0:
            # Daytime: Solar panels actively charging battery
            # Solar peak at 12:00
            solar_intensity = math.sin(math.pi * (hour - 6.0) / 12.0)
            charge_rate = 1.5 * solar_intensity
            dev.battery_level = min(100.0, dev.battery_level + charge_rate)
        else:
            # Nighttime: Gradual discharge to power microcontroller & RF module
            discharge_rate = 0.2 + random.uniform(0.0, 0.05)
            dev.battery_level = max(82.0, dev.battery_level - discharge_rate)

        # Add minor measurement jitter
        jitter = random.uniform(-0.5, 0.5) if self.config.simulation.enable_jitter else 0.0
        return int(round(max(0, min(100, dev.battery_level + jitter))))

    def _calculate_signal(self, dev: SimulatedDeviceState) -> int:
        """Simulates smooth RF / cellular RSSI signal drift."""
        # Markov random walk with mean reversion towards 88%
        drift = random.gauss(0, 1.2) if self.config.simulation.enable_jitter else 0.0
        reversion = (88.0 - dev.signal_strength) * 0.05
        dev.signal_strength = max(65.0, min(99.0, dev.signal_strength + drift + reversion))
        return int(round(dev.signal_strength))

    def generate_historical_dataset(
        self,
        duration_hours: int = 24,
        interval_minutes: int = 15,
        include_incidents: bool = True,
    ) -> List[TelemetryReadingPayload]:
        """
        Generates a chronological time-series historical dataset from (now - duration_hours) up to now.
        Optionally injects realistic past incidents (vegetation sag, night breach).
        """
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(hours=duration_hours)
        total_steps = int((duration_hours * 60) / interval_minutes)

        readings: List[TelemetryReadingPayload] = []

        # Define incident time windows if requested
        # Example incident 1: Vegetation sag on Section 2 starting 18h ago lasting 4h
        veg_start = now - timedelta(hours=min(18, duration_hours - 2))
        veg_end = veg_start + timedelta(hours=4)

        # Example incident 2: Elephant breach on Section 3 starting 6h ago lasting 1h
        breach_start = now - timedelta(hours=min(6, max(1, duration_hours - 1)))
        breach_end = breach_start + timedelta(minutes=50)

        for step in range(total_steps + 1):
            t = start_time + timedelta(minutes=step * interval_minutes)
            if t > now:
                break

            for dev in self.devices.values():
                # Apply simulated past incidents
                original_state = dev.current_state
                if include_incidents:
                    if dev.section_code == "SEC-02" and veg_start <= t <= veg_end:
                        dev.current_state = DeviceOperationalState.VEGETATION_WARNING
                    elif dev.section_code == "SEC-03" and breach_start <= t <= breach_end:
                        dev.current_state = DeviceOperationalState.CRITICAL_BREACH
                    else:
                        dev.current_state = DeviceOperationalState.NORMAL

                r = self.generate_reading_for_device(dev, target_time=t)
                if r is not None:
                    readings.append(r)

                dev.current_state = original_state

        # Restore current state
        self.reset_all_to_normal()
        return readings
