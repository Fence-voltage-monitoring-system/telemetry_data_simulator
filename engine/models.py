"""
Data models representing device telemetry states, readings, and fault conditions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class DeviceOperationalState(str, Enum):
    NORMAL = "normal"
    VEGETATION_WARNING = "vegetation_warning"
    CRITICAL_BREACH = "critical_breach"
    LOW_BATTERY = "low_battery"
    OFFLINE = "offline"

    @classmethod
    def from_str(cls, value: str) -> "DeviceOperationalState":
        val = value.strip().lower()
        for member in cls:
            if member.value == val or member.name.lower() == val:
                return member
        return cls.NORMAL


@dataclass
class TelemetryReadingPayload:
    deviceSerial: str
    voltage: float  # in kV (e.g., 6.84)
    battery: int    # 0 to 100 percentage
    signal: int     # 0 to 100 percentage
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_ingest_dict(self) -> Dict[str, Any]:
        """
        Converts the reading to the exact JSON schema expected by Spring Boot TelemetryIngestRequestDTO.
        """
        return {
            "deviceSerial": self.deviceSerial,
            "voltage": round(self.voltage, 2),
            "battery": int(self.battery),
            "signal": int(self.signal),
        }

    def to_full_dict(self) -> Dict[str, Any]:
        """
        Includes formatted timestamp for logging and historical analysis.
        """
        data = self.to_ingest_dict()
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class SimulatedDeviceState:
    serial: str
    section_code: str
    section_name: str
    fence_code: str
    fence_name: str
    gateway_id: str
    nominal_voltage: float = 6.8
    current_state: DeviceOperationalState = DeviceOperationalState.NORMAL
    battery_level: float = 95.0
    signal_strength: float = 88.0
    last_reading: Optional[TelemetryReadingPayload] = None
    state_start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    state_duration_seconds: Optional[float] = None  # None = indefinite
