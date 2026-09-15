import unittest

from cvc_research.trace import TraceValidationError, validate_trace_records


class TraceValidationTests(unittest.TestCase):
    def valid_record(self, **updates):
        record = {
            "run_id": "run-001",
            "scenario_id": "B01",
            "candidate_id": "PC-001",
            "candidate_version": "abc123",
            "sim_time": 0.0,
            "tick": 0,
            "actor": "subject",
            "record_type": "event",
            "native_type": "support_event",
            "normalized_type": "support",
            "target": "partner",
            "payload": {},
            "seed": 7,
            "wall_clock_ns": 100,
        }
        record.update(updates)
        return record

    def test_valid_trace(self):
        records = [
            self.valid_record(),
            self.valid_record(
                tick=1,
                sim_time=1.0,
                record_type="action",
                native_type="help_partner",
                normalized_type="help",
            ),
        ]
        summary = validate_trace_records(records)
        self.assertEqual(summary["records"], 2)
        self.assertEqual(summary["runs"], 1)
        self.assertEqual(summary["record_types"]["action"], 1)

    def test_missing_required_field_fails(self):
        record = self.valid_record()
        del record["payload"]
        with self.assertRaises(TraceValidationError):
            validate_trace_records([record])

    def test_tick_regression_fails(self):
        records = [self.valid_record(tick=2), self.valid_record(tick=1, sim_time=1.0)]
        with self.assertRaises(TraceValidationError) as context:
            validate_trace_records(records)
        self.assertIn("tick regressed", str(context.exception))

    def test_metadata_change_within_run_fails(self):
        records = [self.valid_record(), self.valid_record(candidate_id="PC-002", tick=1, sim_time=1.0)]
        with self.assertRaises(TraceValidationError) as context:
            validate_trace_records(records)
        self.assertIn("changed scenario/candidate/version metadata", str(context.exception))

    def test_multiple_runs_are_allowed(self):
        records = [self.valid_record(), self.valid_record(run_id="run-002", candidate_id="PC-002")]
        summary = validate_trace_records(records)
        self.assertEqual(summary["runs"], 2)


if __name__ == "__main__":
    unittest.main()
