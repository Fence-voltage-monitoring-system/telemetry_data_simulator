"""
Configuration loader for the Telemetry Data Simulator.
Loads settings, server endpoints, and gateway/fence/device topologies from config.yaml.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


@dataclass
class ServerConfig:
    base_url: str = "http://localhost:8080"
    ingest_endpoint: str = "/api/v1/telemetry/ingest"
    timeout_seconds: int = 5
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0

    @property
    def ingest_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/{self.ingest_endpoint.lstrip('/')}"


@dataclass
class SimulationConfig:
    interval_seconds: int = 60
    stagger_gateways: bool = True
    mode: str = "continuous"
    enable_jitter: bool = True
    simulate_solar_battery: bool = True


@dataclass
class VoltageProfile:
    nominal_kv: float = 6.8
    min_kv: float = 5.5
    max_kv: float = 8.5
    noise_std: float = 0.15


@dataclass
class DeviceConfig:
    serial: str
    section_code: str
    section_name: str
    nominal_voltage: float = 6.8
    initial_state: str = "normal"  # normal, vegetation_warning, critical_breach, dead_battery, offline


@dataclass
class FenceConfig:
    code: str
    name: str
    devices: List[DeviceConfig] = field(default_factory=list)


@dataclass
class GatewayConfig:
    id: str
    name: str
    location: str
    fences: List[FenceConfig] = field(default_factory=list)


@dataclass
class AppConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    voltage_profiles: Dict[str, VoltageProfile] = field(default_factory=dict)
    gateways: List[GatewayConfig] = field(default_factory=list)


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    data = {}
    if config_path is None:
        yaml_path = Path(__file__).parent / "config.yaml"
        json_path = Path(__file__).parent / "config.json"
        if HAS_YAML and yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        elif json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
        elif yaml_path.exists():
            # If HAS_YAML is False but yaml file exists, try basic json fallback
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            except Exception:
                data = {}
    else:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        if path.suffix.lower() == ".json" or not HAS_YAML:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

    # Server config
    server_data = data.get("server", {})
    server = ServerConfig(
        base_url=server_data.get("base_url", "http://localhost:8080"),
        ingest_endpoint=server_data.get("ingest_endpoint", "/api/v1/telemetry/ingest"),
        timeout_seconds=server_data.get("timeout_seconds", 5),
        retry_attempts=server_data.get("retry_attempts", 3),
        retry_delay_seconds=server_data.get("retry_delay_seconds", 1.0),
    )

    # Simulation config
    sim_data = data.get("simulation", {})
    simulation = SimulationConfig(
        interval_seconds=sim_data.get("interval_seconds", 60),
        stagger_gateways=sim_data.get("stagger_gateways", True),
        mode=sim_data.get("mode", "continuous"),
        enable_jitter=sim_data.get("enable_jitter", True),
        simulate_solar_battery=sim_data.get("simulate_solar_battery", True),
    )

    # Voltage profiles
    profiles_data = data.get("voltage_profiles", {})
    voltage_profiles = {}
    for name, p in profiles_data.items():
        voltage_profiles[name] = VoltageProfile(
            nominal_kv=float(p.get("nominal_kv", 6.8)),
            min_kv=float(p.get("min_kv", 5.5)),
            max_kv=float(p.get("max_kv", 8.5)),
            noise_std=float(p.get("noise_std", 0.15)),
        )

    # Gateways & Fences & Devices
    gateways = []
    for gw in data.get("gateways", []):
        fences = []
        for fc in gw.get("fences", []):
            devices = []
            for dev in fc.get("devices", []):
                devices.append(
                    DeviceConfig(
                        serial=dev.get("serial", "UNKNOWN-DEV"),
                        section_code=dev.get("section_code", "SEC-01"),
                        section_name=dev.get("section_name", "Fence Section"),
                        nominal_voltage=float(dev.get("nominal_voltage", 6.8)),
                        initial_state=dev.get("initial_state", "normal"),
                    )
                )
            fences.append(FenceConfig(code=fc.get("code", "FC-01"), name=fc.get("name", "Fence"), devices=devices))
        gateways.append(
            GatewayConfig(
                id=gw.get("id", "GW-01"),
                name=gw.get("name", "Gateway"),
                location=gw.get("location", "Location"),
                fences=fences,
            )
        )

    return AppConfig(
        server=server,
        simulation=simulation,
        voltage_profiles=voltage_profiles,
        gateways=gateways,
    )
