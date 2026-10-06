"""
Integration & Unit Test Suite for Telemetry Simulator
Tests physics models, configuration loading, fault injection, and mock backend ingestion.
"""

from datetime import datetime, timezone
import json
import socket
import threading
import unittest
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

from config_loader import load_config, AppConfig, ServerConfig
from engine.models import DeviceOperationalState, TelemetryReadingPayload
from engine.generator import TelemetryGenerator
from scenarios.presets import AVAILABLE_SCENARIOS, apply_scenario
from client.http_client import TelemetryHttpClient


class MockSpringBootTelemetryHandler(BaseHTTPRequestHandler):
    """Mocks Spring Boot TelemetryController (/api/v1/telemetry/ingest)"""

    registered_serials = {"SN-12345", "SN-E-01001", "SN-E-01002", "SN-E-01003", "SN-E-02001", "SN-E-02002", "SN-E-02003"}
    received_readings = []

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/v1/telemetry/ingest":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            serial = data.get("deviceSerial")
            if serial not in self.registered_serials:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Device not found with serial: {serial}"}).encode("utf-8"))
                return

            MockSpringBootTelemetryHandler.received_readings.append(data)
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response_payload = {
                "id": f"reading-{len(MockSpringBootTelemetryHandler.received_readings)}",
                "deviceSerial": serial,
                "voltageKv": data.get("voltage"),
                "battery": data.get("battery"),
                "signal": data.get("signal"),
                "recordedAt": datetime.now(timezone.utc).isoformat(),
            }
            self.wfile.write(json.dumps(response_payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/actuator/health", "/api/v1/fences"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "UP"}).encode("utf-8"))
        else:
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence server log noise during test
        pass


class TestTelemetrySimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Find a free local port for the mock server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        cls.mock_port = s.getsockname()[1]
        s.close()

        cls.mock_server = HTTPServer(("127.0.0.1", cls.mock_port), MockSpringBootTelemetryHandler)
        cls.server_thread = threading.Thread(target=cls.mock_server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.mock_server.shutdown()
        cls.mock_server.server_close()

    def setUp(self):
        MockSpringBootTelemetryHandler.received_readings.clear()
        self.config = load_config()
        self.config.server.base_url = f"http://127.0.0.1:{self.mock_port}"
        self.generator = TelemetryGenerator(self.config)
        self.client = TelemetryHttpClient(self.config.server)

    def test_config_loading(self):
        self.assertGreater(len(self.config.gateways), 0)
        self.assertGreater(len(self.config.voltage_profiles), 0)
        self.assertIn("SN-12345", self.generator.devices)

    def test_physics_voltage_generation(self):
        dev = self.generator.devices["SN-12345"]

        # Normal state
        r_normal = self.generator.generate_reading_for_device(dev)
        self.assertIsNotNone(r_normal)
        self.assertGreaterEqual(r_normal.voltage, 5.0)
        self.assertLessEqual(r_normal.voltage, 9.0)

        # Breach state
        self.generator.set_device_state("SN-12345", DeviceOperationalState.CRITICAL_BREACH)
        r_breach = self.generator.generate_reading_for_device(dev)
        self.assertIsNotNone(r_breach)
        self.assertLessEqual(r_breach.voltage, 1.5)

        # Vegetation sag
        self.generator.set_device_state("SN-12345", DeviceOperationalState.VEGETATION_WARNING)
        r_veg = self.generator.generate_reading_for_device(dev)
        self.assertIsNotNone(r_veg)
        self.assertGreaterEqual(r_veg.voltage, 3.0)
        self.assertLessEqual(r_veg.voltage, 5.0)

    def test_solar_battery_diurnal_cycle(self):
        dev = self.generator.devices["SN-12345"]

        # Noon time (peak sun 12:00)
        t_noon = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
        r_noon = self.generator.generate_reading_for_device(dev, target_time=t_noon)
        self.assertGreaterEqual(r_noon.battery, 85)

        # Low battery fault
        self.generator.set_device_state("SN-12345", DeviceOperationalState.LOW_BATTERY)
        r_lowbat = self.generator.generate_reading_for_device(dev)
        self.assertLessEqual(r_lowbat.battery, 20)

    def test_scenario_presets_application(self):
        apply_scenario(self.generator, "breach", "SN-E-01001")
        self.assertEqual(self.generator.devices["SN-E-01001"].current_state, DeviceOperationalState.CRITICAL_BREACH)

        apply_scenario(self.generator, "outage", "FC-WILPATPU-01")
        for dev in self.generator.devices.values():
            if dev.fence_code == "FC-WILPATPU-01":
                self.assertEqual(dev.current_state, DeviceOperationalState.CRITICAL_BREACH)

        apply_scenario(self.generator, "normal")
        for dev in self.generator.devices.values():
            self.assertEqual(dev.current_state, DeviceOperationalState.NORMAL)

    def test_end_to_end_http_ingestion(self):
        # Probe server online
        self.assertTrue(self.client.is_backend_online())

        # Send single reading
        reading = self.generator.generate_reading_for_device(self.generator.devices["SN-12345"])
        res = self.client.send_telemetry(reading)
        self.assertTrue(res.success)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(MockSpringBootTelemetryHandler.received_readings), 1)

    def test_batch_and_historical_backfill(self):
        history = self.generator.generate_historical_dataset(duration_hours=6, interval_minutes=30)
        self.assertGreater(len(history), 50)

        batch_res = self.client.send_batch(history[:10])
        self.assertEqual(batch_res.successful, 10)
        self.assertEqual(batch_res.failed, 0)


if __name__ == "__main__":
    unittest.main()
