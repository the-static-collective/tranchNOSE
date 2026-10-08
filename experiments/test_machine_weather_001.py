import unittest
from experiments.machine_weather_001 import observe_window, compare_weather

class WeatherTests(unittest.TestCase):
    def data(self,id,value):
        return dict(window_id=id, source_ref="fixture", start_utc="2026-09-20T00:00:00Z",
                    end_utc="2026-09-20T00:00:01Z",
                    measurements={"hum_hz":{"value":value,"unit":"Hz","sensor_ref":"fixture:meter"}})
    def test_measured_delta_and_receipts(self):
        a=observe_window(self.data("a",60)); b=observe_window(self.data("b",59.5))
        self.assertEqual(compare_weather(a,b)["deltas"]["hum_hz"]["delta"],-0.5)
        self.assertNotEqual(a["sha256"],b["sha256"])
    def test_absence_is_not_zero(self):
        a=observe_window(self.data("a",60))
        b=observe_window({**self.data("b",60),"measurements":{"cpu_celsius":{"value":30,"unit":"C","sensor_ref":"fixture:cpu"}}})
        self.assertEqual(compare_weather(a,b)["deltas"]["hum_hz"]["status"],"unavailable")
    def test_refuses_untyped_and_nonfinite(self):
        with self.assertRaises(ValueError): observe_window(self.data("a",float("nan")))
        with self.assertRaises(ValueError): observe_window({**self.data("a",60),"start_utc":"local"})
    def test_sensor_mismatch_not_numerical_delta(self):
        a=observe_window(self.data("a",60))
        b=observe_window(self.data("b",60))
        b["measurements"]["hum_hz"]["sensor_ref"]="fixture:different"
        self.assertEqual(compare_weather(a,b)["deltas"]["hum_hz"]["status"],"incomparable_provenance")

if __name__ == "__main__": unittest.main()
