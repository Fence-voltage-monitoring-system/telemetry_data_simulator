"""
HTTP REST Client for ingesting fence telemetry readings into Spring Boot backend.
"""

from dataclasses import dataclass, field
import json
import logging
import time
from typing import Any, Dict, List, Optional
import requests

from config_loader import ServerConfig
from engine.models import TelemetryReadingPayload

logger = logging.getLogger("TelemetryHttpClient")


@dataclass
class IngestResult:
    success: bool
    status_code: Optional[int]
    device_serial: str
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    latency_ms: float = 0.0


@dataclass
class BatchIngestResult:
    total: int = 0
    successful: int = 0
    failed: int = 0
    results: List[IngestResult] = field(default_factory=list)
    total_time_ms: float = 0.0


class TelemetryHttpClient:
    def __init__(self, config: ServerConfig, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "NERDC-Elephant-Fence-Gateway-Simulator/1.0",
        })

    def is_backend_online(self) -> bool:
        """Pings backend base URL to check connectivity."""
        try:
            resp = self.session.get(
                f"{self.config.base_url.rstrip('/')}/actuator/health",
                timeout=self.config.timeout_seconds,
            )
            return resp.status_code in (200, 401, 403, 404)
        except requests.RequestException:
            try:
                # Fallback to root or ping endpoint
                resp = self.session.get(
                    self.config.base_url,
                    timeout=self.config.timeout_seconds,
                )
                return True
            except requests.RequestException:
                return False

    def send_telemetry(self, reading: TelemetryReadingPayload) -> IngestResult:
        """
        Transmits a single telemetry reading payload to the backend POST /api/v1/telemetry/ingest endpoint.
        """
        url = self.config.ingest_url
        payload = reading.to_ingest_dict()
        start_time = time.time()

        for attempt in range(1, self.config.retry_attempts + 1):
            try:
                response = self.session.post(
                    url,
                    json=payload,
                    timeout=self.config.timeout_seconds,
                )
                latency_ms = (time.time() - start_time) * 1000

                if response.status_code in (200, 201):
                    try:
                        resp_json = response.json()
                    except json.JSONDecodeError:
                        resp_json = {}
                    return IngestResult(
                        success=True,
                        status_code=response.status_code,
                        device_serial=reading.deviceSerial,
                        response_data=resp_json,
                        latency_ms=round(latency_ms, 1),
                    )
                elif response.status_code == 404:
                    # Device not found in database
                    err_msg = f"Device '{reading.deviceSerial}' not registered in backend database (HTTP 404)"
                    return IngestResult(
                        success=False,
                        status_code=404,
                        device_serial=reading.deviceSerial,
                        error_message=err_msg,
                        latency_ms=round(latency_ms, 1),
                    )
                else:
                    err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    if attempt < self.config.retry_attempts and response.status_code >= 500:
                        time.sleep(self.config.retry_delay_seconds)
                        continue
                    return IngestResult(
                        success=False,
                        status_code=response.status_code,
                        device_serial=reading.deviceSerial,
                        error_message=err_msg,
                        latency_ms=round(latency_ms, 1),
                    )

            except requests.Timeout:
                latency_ms = (time.time() - start_time) * 1000
                if attempt < self.config.retry_attempts:
                    time.sleep(self.config.retry_delay_seconds)
                    continue
                return IngestResult(
                    success=False,
                    status_code=None,
                    device_serial=reading.deviceSerial,
                    error_message=f"Request timed out after {self.config.timeout_seconds}s",
                    latency_ms=round(latency_ms, 1),
                )

            except requests.ConnectionError:
                latency_ms = (time.time() - start_time) * 1000
                return IngestResult(
                    success=False,
                    status_code=None,
                    device_serial=reading.deviceSerial,
                    error_message=f"Cannot connect to backend at {self.config.base_url}. Is Spring Boot running?",
                    latency_ms=round(latency_ms, 1),
                )

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                return IngestResult(
                    success=False,
                    status_code=None,
                    device_serial=reading.deviceSerial,
                    error_message=str(e),
                    latency_ms=round(latency_ms, 1),
                )

        return IngestResult(
            success=False,
            status_code=None,
            device_serial=reading.deviceSerial,
            error_message="Max retries exhausted",
            latency_ms=(time.time() - start_time) * 1000,
        )

    def send_batch(self, readings: List[TelemetryReadingPayload]) -> BatchIngestResult:
        """
        Transmits a collection of telemetry readings sequentially or in batch.
        """
        start_time = time.time()
        results: List[IngestResult] = []
        successful = 0
        failed = 0

        for r in readings:
            res = self.send_telemetry(r)
            results.append(res)
            if res.success:
                successful += 1
            else:
                failed += 1

        total_time_ms = (time.time() - start_time) * 1000
        return BatchIngestResult(
            total=len(readings),
            successful=successful,
            failed=failed,
            results=results,
            total_time_ms=round(total_time_ms, 1),
        )
