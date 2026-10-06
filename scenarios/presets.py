"""
Incident & Fault Simulation Presets.
Enables instant triggering of field conditions: Elephant Breaches, Tree Contact, Low Battery, Outages, etc.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from engine.models import DeviceOperationalState
from engine.generator import TelemetryGenerator


class ScenarioType(str, Enum):
    NORMAL = "normal"
    ELEPHANT_BREACH = "elephant_breach"
    VEGETATION_SAG = "vegetation_sag"
    LOW_BATTERY = "low_battery"
    OFFLINE_DEVICE = "offline_device"
    FENCE_OUTAGE = "fence_outage"


@dataclass
class ScenarioPreset:
    name: str
    description: str
    target_state: DeviceOperationalState
    default_duration_seconds: Optional[float] = None
    affects_all_fence_sections: bool = False


AVAILABLE_SCENARIOS: Dict[str, ScenarioPreset] = {
    "normal": ScenarioPreset(
        name="Healthy Normal",
        description="Restores device/fence to optimal operating parameters (6.5 - 7.5 kV, >90% battery).",
        target_state=DeviceOperationalState.NORMAL,
    ),
    "breach": ScenarioPreset(
        name="Elephant Breach / Fence Cut",
        description="Wire broken or shorted to ground (voltage collapses to 0.0 - 0.5 kV).",
        target_state=DeviceOperationalState.CRITICAL_BREACH,
        default_duration_seconds=300.0,
    ),
    "vegetation": ScenarioPreset(
        name="Vegetation Sag / Ground Touch",
        description="Wet tree branches touching wire causing voltage leakage (voltage drops to 3.5 - 4.5 kV).",
        target_state=DeviceOperationalState.VEGETATION_WARNING,
        default_duration_seconds=600.0,
    ),
    "battery": ScenarioPreset(
        name="Solar Panel Failure / Low Battery",
        description="Solar charging fails and battery drops into critical zone (<15%).",
        target_state=DeviceOperationalState.LOW_BATTERY,
        default_duration_seconds=600.0,
    ),
    "offline": ScenarioPreset(
        name="Communication Loss / Device Offline",
        description="Gateway or sensor stops transmitting packets to test heartbeat timeout.",
        target_state=DeviceOperationalState.OFFLINE,
        default_duration_seconds=300.0,
    ),
    "outage": ScenarioPreset(
        name="Total Energizer Power Outage",
        description="All sections across the target fence collapse to 0.0 kV simultaneously.",
        target_state=DeviceOperationalState.CRITICAL_BREACH,
        default_duration_seconds=300.0,
        affects_all_fence_sections=True,
    ),
}


def apply_scenario(
    generator: TelemetryGenerator,
    scenario_key: str,
    target_serial_or_fence: Optional[str] = None,
    duration_seconds: Optional[float] = None,
) -> str:
    """
    Applies a named scenario to a specific device serial or fence code.
    If target is omitted, applies to the first device found.
    """
    key = scenario_key.lower().strip()
    if key not in AVAILABLE_SCENARIOS:
        raise ValueError(f"Unknown scenario '{key}'. Available: {list(AVAILABLE_SCENARIOS.keys())}")

    preset = AVAILABLE_SCENARIOS[key]
    dur = duration_seconds if duration_seconds is not None else preset.default_duration_seconds

    if key == "normal":
        if target_serial_or_fence:
            if target_serial_or_fence in generator.devices:
                generator.set_device_state(target_serial_or_fence, DeviceOperationalState.NORMAL)
                return f"Device '{target_serial_or_fence}' restored to NORMAL state."
            else:
                cnt = generator.set_fence_state(target_serial_or_fence, DeviceOperationalState.NORMAL)
                return f"Fence '{target_serial_or_fence}' ({cnt} devices) restored to NORMAL state."
        else:
            generator.reset_all_to_normal()
            return "All fences and devices restored to NORMAL state."

    if preset.affects_all_fence_sections:
        # Fence-wide scenario
        fence_code = target_serial_or_fence or "FC-WILPATPU-01"
        cnt = generator.set_fence_state(fence_code, preset.target_state, duration_seconds=dur)
        return f"Applied '{preset.name}' to fence '{fence_code}' ({cnt} sections affected)."
    else:
        # Device-specific scenario
        target_serial = target_serial_or_fence
        if not target_serial or target_serial not in generator.devices:
            # Default to the first available device
            target_serial = next(iter(generator.devices.keys()))
        generator.set_device_state(target_serial, preset.target_state, duration_seconds=dur)
        return f"Applied '{preset.name}' to device '{target_serial}' (duration: {dur}s)."
