# NERDC Remote Elephant Fence Telemetry Simulator

A realistic physics-based telemetry data simulator for the **Remote Elephant Fence Monitoring System**.

This tool simulates IoT gateways and fence monitoring sensor nodes across Sri Lanka transmitting real-time voltage, battery, and signal data to the Spring Boot backend (`POST /api/v1/telemetry/ingest`).

---

## ⚡ Features

- **Physics-Based Voltage Engine**: Simulates energizer pulse oscillations, Gaussian environmental noise, vegetation leakage sag, and catastrophic wire breach collapses.
- **24-Hour Solar Diurnal Battery Cycle**: Accurately simulates solar panel daytime charging ($06:00-18:00$) and gradual nighttime discharge.
- **Smooth RF Signal Drift**: Markov random walk modeling weather fading and cellular signal variance.
- **Interactive Live Fault Injection**: Trigger real-time elephant breaches, tree contact sag, battery failure, or communication loss via terminal hotkeys.
- **Historical Backfill Engine**: Seed 24 hours, 7 days, or 30 days of historical data into the backend database to test 24h trend charts and PDF/CSV analytics reports.
- **Multi-Gateway & Multi-Fence Topologies**: Simulates hubs in Anuradhapura, Minneriya, Polonnaruwa, etc.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd telemetry_simulator
pip install -r requirements.txt
```

### 2. Run the Interactive Simulator (Default 10s Cycle)
```bash
python3 main.py
```

### 3. Run Real-World 15-Minute Cycle
```bash
python3 main.py --interval 900
```

---

## 🎮 Interactive Live Hotkeys

While the simulator is running in continuous mode, you can type commands into the terminal:

| Key / Command | Action | Effect on System |
| :--- | :--- | :--- |
| `1 [serial]` / `breach` | **Elephant Breach** | Drops voltage to $0.1\text{ kV}$ (Triggers Red Alarm & 3D wire alert) |
| `2 [serial]` / `veg` | **Vegetation Sag** | Drops voltage to $3.8\text{ kV}$ (Triggers Amber Warning) |
| `3 [serial]` / `battery` | **Low Battery** | Drains battery to $<15\%$ (Triggers Maintenance alert) |
| `4 [serial]` / `offline` | **Device Offline** | Halts transmission for node (Tests heartbeat timeout) |
| `outage` | **Fence Outage** | Collapses all sections of a fence simultaneously |
| `r` / `reset` | **Restore Normal** | Resets all fences and devices back to healthy state |
| `h` / `help` | **Help Menu** | Displays interactive commands |
| `q` / `quit` | **Quit** | Gracefully stops the simulator |

---

## 📊 Historical Backfill Mode

Populate historical telemetry into your backend database for testing analytics charts:

```bash
# Backfill past 24 hours of telemetry (15-min intervals)
python3 main.py --backfill 24h

# Backfill past 7 days of telemetry
python3 main.py --backfill 7d
```

---

## 🛠️ CLI Options

```text
usage: main.py [-h] [--config CONFIG] [--mode {continuous,once,backfill,scenario}]
               [--interval INTERVAL] [--backfill BACKFILL]
               [--scenario {normal,breach,vegetation,battery,offline,outage}]
               [--target TARGET] [--url URL]

options:
  --config CONFIG       Path to custom config.yaml file
  --mode MODE           Simulator execution mode (default: continuous)
  --interval INTERVAL   Telemetry push interval in seconds (default: 10s)
  --backfill BACKFILL   Generate past historical data (e.g. '24h', '7d', '30d')
  --scenario SCENARIO   Trigger a specific test scenario preset
  --target TARGET       Target device serial (e.g. SN-12345) or fence code (e.g. FC-WILPATPU-01)
  --url URL             Override backend base URL (default: http://localhost:8080)
```
