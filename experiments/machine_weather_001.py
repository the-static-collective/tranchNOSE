"""MACHINE-WEATHER-001: bounded, caller-supplied telemetry comparison.

Not a hardware sensor driver, optical-field inference, causal model, or control loop.
No system inspection, continuous capture, external I/O, or changes to the 001a field experiment.
"""
from __future__ import annotations
from hashlib import sha256
import json
from math import isfinite

MEASURES = ("cpu_celsius", "ambient_celsius", "hum_hz", "disk_bytes_per_second")


def observe_window(window: dict) -> dict:
    if not isinstance(window, dict) or set(window) != {"window_id", "source_ref", "start_utc", "end_utc", "measurements"}:
        raise ValueError("explicit window identity, time and measurements required")
    for key in ("window_id", "source_ref", "start_utc", "end_utc"):
        value = window[key]
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            raise ValueError(f"invalid {key}")
    from datetime import datetime
    def parse(s):
        if not s.endswith("Z"):
            raise ValueError("explicit UTC required")
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    if parse(window["end_utc"]) < parse(window["start_utc"]):
        raise ValueError("negative duration")
    raw = window["measurements"]
    if not isinstance(raw, dict) or not raw or set(raw) - set(MEASURES):
        raise ValueError("unknown or absent measurement keys")
    typed = {}
    for name, datum in raw.items():
        if not isinstance(datum, dict) or set(datum) != {"value", "unit", "sensor_ref"}:
            raise ValueError("value, unit and sensor reference required")
        val = datum["value"]
        units = {"cpu_celsius": "C", "ambient_celsius": "C", "hum_hz": "Hz", "disk_bytes_per_second": "B/s"}
        if type(val) not in (int, float) or not isfinite(val) or datum["unit"] != units[name]:
            raise ValueError("finite typed measurement required")
        if name in ("hum_hz", "disk_bytes_per_second") and val < 0:
            raise ValueError("negative frequency/throughput")
        sensor = datum["sensor_ref"]
        if not isinstance(sensor, str) or not sensor.strip():
            raise ValueError("sensor provenance required")
        typed[name] = {"value": float(val), "unit": units[name], "sensor_ref": sensor}
    payload = {"schema": "tranchNOSE.machine-weather/0.1", **{k:window[k] for k in
               ("window_id", "source_ref", "start_utc", "end_utc")}, "measurements": typed,
               "non_claims": ["not independent proof of sensor accuracy", "not optical state",
                              "correlation does not imply causation", "no control authority"]}
    payload["sha256"] = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return payload


def compare_weather(first: dict, second: dict) -> dict:
    if first.get("schema") != "tranchNOSE.machine-weather/0.1" or second.get("schema") != first["schema"]:
        raise ValueError("two typed observations required")
    delta = {}
    for key in sorted(set(first["measurements"]) | set(second["measurements"])):
        a,b=first["measurements"].get(key),second["measurements"].get(key)
        if a is None or b is None:
            delta[key]={"status":"unavailable"}
        elif (a["unit"],a["sensor_ref"]) != (b["unit"],b["sensor_ref"]):
            delta[key]={"status":"incomparable_provenance"}
        else:
            delta[key]={"status":"computed","delta":b["value"]-a["value"],"unit":a["unit"]}
    return {"schema":"tranchNOSE.machine-weather-delta/0.1","first_ref":first["sha256"],
            "second_ref":second["sha256"],"deltas":delta,
            "non_claim":"numeric delta is not a diagnosis or permission to change equipment"}
