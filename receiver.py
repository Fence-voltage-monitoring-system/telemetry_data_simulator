#!/usr/bin/env python3
"""
==============================================================================
Mock Backend Ingestion Server
==============================================================================
A lightweight HTTP test server running on port 8080 (or custom port).
Receives and displays incoming telemetry POST requests from the simulator in real time.
"""

import argparse
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"


class TelemetryReceiverHandler(BaseHTTPRequestHandler):
    reading_count = 0

    def do_POST(self):
        if self.path == "/api/v1/telemetry/ingest":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
                return

            TelemetryReceiverHandler.reading_count += 1
            rec_id = TelemetryReceiverHandler.reading_count
            timestamp = datetime.now().strftime("%H:%M:%S")

            serial = payload.get("deviceSerial", "UNKNOWN")
            voltage = payload.get("voltage", 0.0)
            battery = payload.get("battery", 0)
            signal = payload.get("signal", 0)

            # Determine voltage status color
            if voltage >= 5.0:
                v_badge = f"{Color.GREEN}{voltage:0.2f} kV (HEALTHY){Color.RESET}"
            elif voltage >= 3.0:
                v_badge = f"{Color.YELLOW}{voltage:0.2f} kV (WARNING - SAG){Color.RESET}"
            else:
                v_badge = f"{Color.RED}{voltage:0.2f} kV (CRITICAL - BREACH){Color.RESET}"

            print(f"\n{Color.CYAN}📥 [HTTP POST #{rec_id} @ {timestamp}] /api/v1/telemetry/ingest{Color.RESET}")
            print(f"   ├─ Device Serial : {Color.BOLD}{serial}{Color.RESET}")
            print(f"   ├─ Voltage       : {v_badge}")
            print(f"   ├─ Battery       : {battery}%")
            print(f"   ├─ Signal        : {signal}%")
            print(f"   └─ Raw Payload   : {Color.DIM}{json.dumps(payload)}{Color.RESET}")

            # Send 201 Created Response
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response_data = {
                "id": str(rec_id),
                "deviceSerial": serial,
                "voltageKv": voltage,
                "battery": battery,
                "signal": signal,
                "status": "RECORDED",
                "recordedAt": datetime.now(timezone.utc).isoformat(),
            }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            print(f"   {Color.GREEN}📤 Responded HTTP 201 Created (ID: {rec_id}){Color.RESET}")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_GET(self):
        if self.path in ("/actuator/health", "/api/v1/fences", "/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "UP", "service": "telemetry-backend-mock"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Override default server log formatting for clean output
        pass


def main():
    parser = argparse.ArgumentParser(description="NERDC Telemetry Mock Backend Ingestion Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    args = parser.parse_args()

    server_address = ("", args.port)
    try:
        httpd = HTTPServer(server_address, TelemetryReceiverHandler)
    except OSError as e:
        print(f"{Color.RED}Error binding to port {args.port}: {e}{Color.RESET}")
        print(f"Try running with a different port e.g. --port 8081")
        sys.exit(1)

    print(f"""{Color.GREEN}{Color.BOLD}
================================================================================
 🌐 NERDC TELEMETRY INGESTION SERVER LISTENING ON PORT {args.port} 🌐
================================================================================{Color.RESET}
 Endpoint: http://localhost:{args.port}/api/v1/telemetry/ingest
 Waiting for incoming telemetry packets from Gateways...
 (Press Ctrl+C to stop)
""")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Stopping server.{Color.RESET}")
        httpd.server_close()


if __name__ == "__main__":
    main()
