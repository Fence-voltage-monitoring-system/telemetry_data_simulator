#!/usr/bin/env python3
"""
==============================================================================
Remote Elephant Fence Monitoring System - Telemetry Data Simulator
NERDC Industrial Training Project
==============================================================================
Simulates gateways and fence monitoring devices transmitting real-time & historical
telemetry data to the Spring Boot backend API.
"""

import argparse
from datetime import datetime, timezone
import json
import os
import sys
import threading
import time
from typing import List, Optional

from config_loader import AppConfig, load_config
from engine.generator import TelemetryGenerator
from engine.models import DeviceOperationalState, TelemetryReadingPayload
from client.http_client import IngestResult, TelemetryHttpClient
from scenarios.presets import AVAILABLE_SCENARIOS, apply_scenario

# ==============================================================================
# ANSI Terminal Color Helpers
# ==============================================================================
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"


def print_banner():
    banner = f"""{Color.CYAN}{Color.BOLD}
================================================================================
 ⚡ NERDC REMOTE ELEPHANT FENCE TELEMETRY SIMULATOR ⚡
================================================================================{Color.RESET}
 {Color.DIM}Simulating Gateways, Solar Nodes, and Physics Telemetry across Sri Lanka{Color.RESET}
"""
    print(banner)


def format_state_badge(state: DeviceOperationalState) -> str:
    if state == DeviceOperationalState.NORMAL:
        return f"{Color.GREEN}{Color.BOLD}[ NORMAL ]{Color.RESET}"
    elif state == DeviceOperationalState.VEGETATION_WARNING:
        return f"{Color.YELLOW}{Color.BOLD}[ WARNING]{Color.RESET}"
    elif state == DeviceOperationalState.CRITICAL_BREACH:
        return f"{Color.RED}{Color.BOLD}[ BREACH ]{Color.RESET}"
    elif state == DeviceOperationalState.LOW_BATTERY:
        return f"{Color.MAGENTA}{Color.BOLD}[ LOW-BAT]{Color.RESET}"
    elif state == DeviceOperationalState.OFFLINE:
        return f"{Color.DIM}[ OFFLINE]{Color.RESET}"
    return f"[{state.value}]"


def print_status_table(
    generator: TelemetryGenerator,
    results: List[IngestResult],
    cycle_num: int,
    interval_sec: float,
):
    print(f"\n{Color.BOLD}===================================================================================================={Color.RESET}")
    print(f"{Color.BOLD} 📡 TELEMETRY CYCLE #{cycle_num} [{datetime.now().strftime('%H:%M:%S')}] | TRANSMISSION INTERVAL: {interval_sec}s{Color.RESET}")
    print(f"{Color.BOLD}===================================================================================================={Color.RESET}")

    result_map = {r.device_serial: r for r in results}

    # Group devices by Gateway
    for gw in generator.config.gateways:
        print(f"\n{Color.CYAN}{Color.BOLD}► GATEWAY: {gw.id} ({gw.name} - {gw.location}){Color.RESET}")
        print(f"  {'DEVICE':<12} {'FENCE':<16} {'SECTION':<20} {'STATUS':<12} {'VOLTAGE':<10} {'BATTERY':<10} {'SIGNAL':<8} {'INGEST RESULT'}")
        print("  " + "-" * 98)

        for fence in gw.fences:
            for dev_cfg in fence.devices:
                dev = generator.devices.get(dev_cfg.serial)
                if not dev:
                    continue
                state_badge = format_state_badge(dev.current_state)
                r = result_map.get(dev.serial)

                if dev.last_reading:
                    v_str = f"{dev.last_reading.voltage:0.2f} kV"
                    b_str = f"{dev.last_reading.battery}%"
                    s_str = f"{dev.last_reading.signal}%"
                else:
                    v_str = "---"
                    b_str = "---"
                    s_str = "---"

                if r is None:
                    res_str = f"{Color.DIM}Offline (Skipped){Color.RESET}"
                elif r.success:
                    res_str = f"{Color.GREEN}✓ 201 Created ({r.latency_ms}ms){Color.RESET}"
                elif r.status_code == 404:
                    res_str = f"{Color.YELLOW}⚠ 404 (Unseeded Serial){Color.RESET}"
                else:
                    res_str = f"{Color.RED}✗ {r.error_message or 'Error'}{Color.RESET}"

                print(
                    f"  {dev.serial:<12} {dev.fence_code:<16} {dev.section_code + ' (' + dev.section_name[:10] + '.)':<20} "
                    f"{state_badge:<21} {v_str:<10} {b_str:<10} {s_str:<8} {res_str}"
                )


def print_interactive_help():
    print(f"\n{Color.BOLD}⚡ Interactive Hotkeys (Type command & press Enter):{Color.RESET}")
    print(f"  {Color.RED}[1] breach <serial>{Color.RESET}   : Trigger Elephant Breach on section (voltage -> 0 kV)")
    print(f"  {Color.YELLOW}[2] veg <serial>{Color.RESET}      : Simulate Vegetation Sag (voltage -> 3.8 kV)")
    print(f"  {Color.MAGENTA}[3] battery <serial>{Color.RESET}  : Simulate Low Battery (<15%)")
    print(f"  {Color.DIM}[4] offline <serial>{Color.RESET}  : Simulate Device Communication Loss")
    print(f"  {Color.GREEN}[r] reset{Color.RESET}             : Restore ALL devices to healthy NORMAL")
    print(f"  {Color.CYAN}[h] help{Color.RESET}              : Show this help menu")
    print(f"  {Color.WHITE}[q] quit{Color.RESET}              : Stop simulator\n")


# ==============================================================================
# Interactive Command Handler Thread
# ==============================================================================
def start_interactive_listener(generator: TelemetryGenerator, stop_event: threading.Event):
    def listener():
        while not stop_event.is_set():
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                cmd = line.strip().lower()
                if not cmd:
                    continue

                tokens = cmd.split()
                action = tokens[0]
                target = tokens[1] if len(tokens) > 1 else None

                if action in ("q", "quit", "exit"):
                    print(f"\n{Color.YELLOW}Stopping simulator...{Color.RESET}")
                    stop_event.set()
                    break
                elif action in ("h", "help", "?"):
                    print_interactive_help()
                elif action in ("r", "reset", "normal"):
                    msg = apply_scenario(generator, "normal", target)
                    print(f"{Color.GREEN}➜ {msg}{Color.RESET}")
                elif action in ("1", "breach", "cut"):
                    msg = apply_scenario(generator, "breach", target)
                    print(f"{Color.RED}➜ {msg}{Color.RESET}")
                elif action in ("2", "veg", "vegetation", "sag"):
                    msg = apply_scenario(generator, "vegetation", target)
                    print(f"{Color.YELLOW}➜ {msg}{Color.RESET}")
                elif action in ("3", "bat", "battery", "lowbat"):
                    msg = apply_scenario(generator, "battery", target)
                    print(f"{Color.MAGENTA}➜ {msg}{Color.RESET}")
                elif action in ("4", "offline", "dead"):
                    msg = apply_scenario(generator, "offline", target)
                    print(f"{Color.DIM}➜ {msg}{Color.RESET}")
                elif action in ("outage", "blackout"):
                    msg = apply_scenario(generator, "outage", target)
                    print(f"{Color.RED}➜ {msg}{Color.RESET}")
                else:
                    print(f"{Color.YELLOW}Unknown command '{cmd}'. Type 'h' for help.{Color.RESET}")
            except Exception as e:
                if stop_event.is_set():
                    break
                print(f"Error in command listener: {e}")

    t = threading.Thread(target=listener, daemon=True)
    t.start()
    return t


# ==============================================================================
# Asynchronous Gateway Worker & Dispatch Display
# ==============================================================================
print_lock = threading.Lock()


def print_gateway_dispatch(
    generator: TelemetryGenerator,
    gw_config,
    results: List[IngestResult],
    cycle_num: int,
    interval_sec: float,
):
    with print_lock:
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"\n{Color.MAGENTA}{Color.BOLD}----------------------------------------------------------------------------------------------------{Color.RESET}")
        print(f"📡 {Color.BOLD}[{timestamp}] GATEWAY DISPATCH: {Color.CYAN}{gw_config.id}{Color.RESET} ({gw_config.name} | {gw_config.location}) - Cycle #{cycle_num}")
        print(f"{Color.MAGENTA}{Color.BOLD}----------------------------------------------------------------------------------------------------{Color.RESET}")
        print(f"  {'DEVICE':<12} {'FENCE':<16} {'SECTION':<20} {'STATUS':<12} {'VOLTAGE':<10} {'BATTERY':<10} {'SIGNAL':<8} {'INGEST RESULT'}")
        print("  " + "-" * 98)

        result_map = {r.device_serial: r for r in results}

        for fence in gw_config.fences:
            for dev_cfg in fence.devices:
                dev = generator.devices.get(dev_cfg.serial)
                if not dev:
                    continue
                state_badge = format_state_badge(dev.current_state)
                r = result_map.get(dev.serial)

                if dev.last_reading:
                    v_str = f"{dev.last_reading.voltage:0.2f} kV"
                    b_str = f"{dev.last_reading.battery}%"
                    s_str = f"{dev.last_reading.signal}%"
                else:
                    v_str = "---"
                    b_str = "---"
                    s_str = "---"

                if r is None:
                    res_str = f"{Color.DIM}Offline (Skipped){Color.RESET}"
                elif r.success:
                    res_str = f"{Color.GREEN}✓ 201 Created ({r.latency_ms}ms){Color.RESET}"
                elif r.status_code == 404:
                    res_str = f"{Color.YELLOW}⚠ 404 (Unseeded Serial){Color.RESET}"
                else:
                    res_str = f"{Color.RED}✗ {r.error_message or 'Error'}{Color.RESET}"

                print(
                    f"  {dev.serial:<12} {dev.fence_code:<16} {dev.section_code + ' (' + dev.section_name[:10] + '.)':<20} "
                    f"{state_badge:<21} {v_str:<10} {b_str:<10} {s_str:<8} {res_str}"
                )


def run_continuous_simulation(config: AppConfig, interval: float):
    generator = TelemetryGenerator(config)
    client = TelemetryHttpClient(config.server)

    num_gateways = len(config.gateways)
    stagger_offset = (interval / num_gateways) if (config.simulation.stagger_gateways and num_gateways > 0) else 0.0

    print_banner()
    print(f"Connecting to Backend Endpoint: {Color.BOLD}{config.server.ingest_url}{Color.RESET}")
    print(f"Active Gateways ({num_gateways}): {[gw.id for gw in config.gateways]}")
    print(f"Total Monitored Sections across Sri Lanka: {len(generator.devices)}")
    print(f"Each Gateway Transmission Cycle: {Color.BOLD}{interval}s{Color.RESET} (Staggered every {stagger_offset:0.1f}s)")

    # Backend Health Probe
    is_online = client.is_backend_online()
    if is_online:
        print(f"Backend Server Status: {Color.GREEN}ONLINE (Ready for Ingest){Color.RESET}")
    else:
        print(f"Backend Server Status: {Color.YELLOW}OFFLINE / UNREACHABLE (Will log requests locally and retry){Color.RESET}")

    print_interactive_help()

    stop_event = threading.Event()
    start_interactive_listener(generator, stop_event)

    gateway_threads = []

    def make_gateway_worker(gw, gw_idx, initial_delay):
        def worker():
            # Initial phase delay to stagger transmissions across the 60-second window
            if initial_delay > 0:
                for _ in range(int(initial_delay * 10)):
                    if stop_event.is_set():
                        return
                    time.sleep(0.1)

            cycle_num = 1
            while not stop_event.is_set():
                # 1. Generate readings for this specific gateway's connected devices
                readings = generator.generate_readings_for_gateway(gw.id)

                # 2. Dispatch batch to backend
                batch_result = client.send_batch(readings)

                # 3. Print the gateway's live transmission card
                print_gateway_dispatch(generator, gw, batch_result.results, cycle_num, interval)

                cycle_num += 1

                # 4. Sleep for the gateway's full 60-second cycle
                for _ in range(int(interval * 10)):
                    if stop_event.is_set():
                        return
                    time.sleep(0.1)

        return worker

    # Launch an independent thread for each Gateway
    for idx, gw in enumerate(config.gateways):
        init_delay = idx * stagger_offset
        t = threading.Thread(
            target=make_gateway_worker(gw, idx, init_delay),
            name=f"Worker-{gw.id}",
            daemon=True,
        )
        gateway_threads.append(t)
        t.start()

    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Simulation halted by user (Ctrl+C). Exiting.{Color.RESET}")
        stop_event.set()


def run_historical_backfill(config: AppConfig, duration_str: str, interval_min: int = 15):
    """
    Backfills past telemetry readings for testing historical graphs and analytics.
    """
    # Parse duration string e.g. '24h', '7d', '30d'
    duration_str = duration_str.lower().strip()
    if duration_str.endswith("h"):
        hours = int(duration_str[:-1])
    elif duration_str.endswith("d"):
        hours = int(duration_str[:-1]) * 24
    else:
        hours = int(duration_str)

    generator = TelemetryGenerator(config)
    client = TelemetryHttpClient(config.server)

    print_banner()
    print(f"{Color.BOLD}Generating Historical Backfill Dataset...{Color.RESET}")
    print(f"Duration: {hours} hours ({hours/24:.1f} days) at {interval_min}-minute resolution.")

    readings = generator.generate_historical_dataset(
        duration_hours=hours,
        interval_minutes=interval_min,
        include_incidents=True,
    )

    print(f"Generated {Color.CYAN}{len(readings)}{Color.RESET} historical data points across {len(generator.devices)} devices.")
    print(f"Transmitting batch to {config.server.ingest_url}...")

    success_cnt = 0
    fail_cnt = 0
    start_time = time.time()

    for idx, r in enumerate(readings, 1):
        res = client.send_telemetry(r)
        if res.success:
            success_cnt += 1
        else:
            fail_cnt += 1

        if idx % 25 == 0 or idx == len(readings):
            pct = (idx / len(readings)) * 100
            sys.stdout.write(f"\rProgress: [{idx}/{len(readings)}] ({pct:0.1f}%) | Success: {success_cnt} | Failed: {fail_cnt}")
            sys.stdout.flush()

    total_time = time.time() - start_time
    print(f"\n\n{Color.GREEN}{Color.BOLD}✓ Backfill Complete!{Color.RESET}")
    print(f"Total Sent: {len(readings)} | Success: {success_cnt} | Failed: {fail_cnt} | Time: {total_time:0.1f}s\n")


def run_single_scenario(config: AppConfig, scenario_name: str, target: Optional[str]):
    generator = TelemetryGenerator(config)
    client = TelemetryHttpClient(config.server)

    print_banner()
    msg = apply_scenario(generator, scenario_name, target)
    print(f"{Color.CYAN}➜ {msg}{Color.RESET}\n")

    readings = generator.generate_all_readings()
    batch_result = client.send_batch(readings)
    print_status_table(generator, batch_result.results, 1, 0.0)


def run_preview(config: AppConfig):
    """Generates and prints sample JSON payloads directly to stdout for inspection."""
    generator = TelemetryGenerator(config)
    print_banner()
    print(f"{Color.BOLD}Telemetry Payload JSON Preview (Grouped by Gateway):{Color.RESET}\n")

    for gw in config.gateways:
        print(f"{Color.BOLD}{Color.MAGENTA}======================================================================{Color.RESET}")
        print(f"{Color.BOLD}{Color.MAGENTA}📡 GATEWAY: {gw.id} | {gw.name} ({gw.location}){Color.RESET}")
        print(f"{Color.BOLD}{Color.MAGENTA}======================================================================{Color.RESET}")

        for fence in gw.fences:
            print(f"\n  {Color.CYAN}🏞️  FENCE: {fence.code} - {fence.name}{Color.RESET}")
            for dev_cfg in fence.devices:
                dev = generator.devices.get(dev_cfg.serial)
                if not dev:
                    continue
                r = generator.generate_reading_for_device(dev)
                if r:
                    print(f"    {Color.BOLD}🔌 Section: {dev.section_code} ({dev.section_name}) | Serial: {r.deviceSerial}{Color.RESET}")
                    print(json.dumps(r.to_full_dict(), indent=6))
                    print()


# ==============================================================================
# Main Entrypoint
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="NERDC Remote Elephant Fence Telemetry Data Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom config.yaml file",
    )
    parser.add_argument(
        "--mode",
        choices=["continuous", "once", "backfill", "scenario", "preview"],
        default="continuous",
        help="Simulator execution mode (default: continuous)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print formatted JSON telemetry payloads without transmitting",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Telemetry push interval in seconds (default: 10s from config)",
    )
    parser.add_argument(
        "--backfill",
        type=str,
        default=None,
        help="Generate past historical data (e.g. '24h', '7d', '30d')",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        choices=list(AVAILABLE_SCENARIOS.keys()),
        default=None,
        help="Trigger a specific test scenario preset",
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Target device serial (e.g. SN-12345) or fence code (e.g. FC-WILPATPU-01)",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Override backend base URL (e.g. http://localhost:8080)",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    if args.url:
        config.server.base_url = args.url

    interval = args.interval if args.interval is not None else float(config.simulation.interval_seconds)

    # Route based on flags
    if args.preview or args.mode == "preview":
        run_preview(config)
    elif args.backfill:
        run_historical_backfill(config, args.backfill)
    elif args.scenario:
        run_single_scenario(config, args.scenario, args.target)
    elif args.mode == "once":
        run_single_scenario(config, "normal", None)
    else:
        run_continuous_simulation(config, interval)


if __name__ == "__main__":
    main()
