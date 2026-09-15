from __future__ import annotations

import unittest

from lifelike_min.exp007_challenger import EligibilityTraceCharacter
from lifelike_min.exp007_evaluation import (
    DisabledEligibilityCharacter,
    ImmediateExpiryCharacter,
    ablation_context_leak,
    action_order_invariance,
    bounded_capacity,
    cross_context,
    delayed_negative,
    delayed_positive,
    expired_trace,
    historical_regressions,
    immediate_control,
    irrelevant_outcome,
    multiple_candidates,
    renderer_invariance,
)


class Exp007DelayedCreditTests(unittest.TestCase):
    def test_positive_delay_lengths(self) -> None:
        for delay in (1, 3, 8):
            with self.subTest(delay=delay):
                self.assertTrue(delayed_positive(EligibilityTraceCharacter, delay)["passed"])

    def test_negative_delay_lengths(self) -> None:
        for delay in (1, 3, 8):
            with self.subTest(delay=delay):
                self.assertTrue(delayed_negative(EligibilityTraceCharacter, delay)["passed"])

    def test_cross_context_does_not_steal_credit(self) -> None:
        self.assertTrue(cross_context(EligibilityTraceCharacter)["passed"])

    def test_multiple_context_candidates_remain_isolated(self) -> None:
        self.assertTrue(multiple_candidates(EligibilityTraceCharacter)["passed"])

    def test_irrelevant_outcome_does_not_leak_reward(self) -> None:
        self.assertTrue(irrelevant_outcome(EligibilityTraceCharacter)["passed"])

    def test_immediate_learning_remains_compatible(self) -> None:
        self.assertTrue(immediate_control(EligibilityTraceCharacter)["passed"])

    def test_trace_expires(self) -> None:
        self.assertTrue(expired_trace(EligibilityTraceCharacter)["passed"])

    def test_trace_capacity_is_bounded(self) -> None:
        self.assertTrue(bounded_capacity(EligibilityTraceCharacter)["passed"])

    def test_action_order_is_not_the_learning_rule(self) -> None:
        self.assertTrue(action_order_invariance(EligibilityTraceCharacter)["passed"])

    def test_renderer_remains_noncausal(self) -> None:
        self.assertTrue(renderer_invariance(EligibilityTraceCharacter)["passed"])

    def test_all_historical_promoted_behaviors_survive(self) -> None:
        rows = historical_regressions(EligibilityTraceCharacter)
        failures = [name for name, row in rows.items() if not row["passed"]]
        self.assertEqual(failures, [])

    def test_primary_causal_ablation_removes_delayed_credit(self) -> None:
        self.assertFalse(delayed_positive(DisabledEligibilityCharacter, 3)["passed"])
        self.assertFalse(delayed_positive(ImmediateExpiryCharacter, 3)["passed"])

    def test_context_blind_ablation_leaks_credit(self) -> None:
        from lifelike_min.exp007_evaluation import ContextBlindCharacter

        self.assertTrue(ablation_context_leak(EligibilityTraceCharacter)["passed"])
        self.assertFalse(ablation_context_leak(ContextBlindCharacter)["passed"])


if __name__ == "__main__":
    unittest.main()
