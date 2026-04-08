"""Test suite for ML Governance Automation module."""

import numpy as np
import pandas as pd
from ml_governance.drift_bias_automation import (
    detect_calibration_drift,
    detect_feature_bias,
    detect_label_bias,
    evaluate_retrain_trigger,
    compute_explainability_metrics,
    run_ml_governance_audit
)
import unittest
import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))


class TestDriftDetection(unittest.TestCase):
    """Test calibration drift detection."""

    def test_no_drift_identical_distributions(self):
        """Drift should not be detected for identical distributions."""
        outputs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        actuals = [0, 0, 0, 0, 1, 1, 1, 1, 1]

        result = detect_calibration_drift(
            outputs, actuals, outputs, actuals, drift_threshold=0.15)

        self.assertFalse(result["drift_detected"])
        self.assertLess(result["drift_magnitude"], 0.15)

    def test_drift_detected_different_calibration(self):
        """Drift should be detected for poorly calibrated models."""
        current_outputs = [0.9] * 10  # Overconfident
        current_actuals = [0] * 10

        reference_outputs = [0.5] * 10  # Well calibrated
        reference_actuals = [0] * 10

        result = detect_calibration_drift(
            current_outputs, current_actuals,
            reference_outputs, reference_actuals,
            drift_threshold=0.15
        )

        self.assertTrue(result["drift_detected"])
        self.assertGreater(result["drift_magnitude"], 0.15)

    def test_ece_computation(self):
        """ECE should be bounded between 0 and 1."""
        outputs = np.random.uniform(0, 1, 100).tolist()
        actuals = (np.random.uniform(0, 1, 100) > 0.5).astype(int).tolist()

        result = detect_calibration_drift(outputs, actuals, outputs, actuals)

        self.assertGreaterEqual(result["ece_current"], 0)
        self.assertLessEqual(result["ece_current"], 1)
        self.assertEqual(result["action"], "MONITOR")


class TestFeatureBias(unittest.TestCase):
    """Test feature distribution bias detection."""

    def test_no_bias_identical_distributions(self):
        """No bias should be detected for identical distributions."""
        dist = pd.Series(np.random.normal(0, 1, 100))

        result = detect_feature_bias(
            {"feature_1": dist},
            {"feature_1": dist},
            bias_threshold=0.25
        )

        self.assertFalse(result["bias_detected"])
        self.assertEqual(len(result["biased_features"]), 0)

    def test_bias_detected_shifted_distribution(self):
        """Bias should be detected for shifted distributions."""
        current = pd.Series(np.random.normal(5, 1, 100))  # Mean = 5
        reference = pd.Series(np.random.normal(0, 1, 100))  # Mean = 0

        result = detect_feature_bias(
            {"feature_1": current},
            {"feature_1": reference},
            bias_threshold=0.10
        )

        self.assertTrue(result["bias_detected"])
        self.assertEqual(len(result["biased_features"]), 1)
        self.assertGreater(result["max_ks_statistic"], 0.10)

    def test_multiple_features_audit(self):
        """Should audit multiple features correctly."""
        current = {
            "feat_1": pd.Series(np.random.normal(0, 1, 100)),
            "feat_2": pd.Series(np.random.normal(5, 1, 100)),  # Biased
            "feat_3": pd.Series(np.random.normal(0, 1, 100))
        }
        reference = {
            "feat_1": pd.Series(np.random.normal(0, 1, 100)),
            "feat_2": pd.Series(np.random.normal(0, 1, 100)),
            "feat_3": pd.Series(np.random.normal(0, 1, 100))
        }

        result = detect_feature_bias(current, reference, bias_threshold=0.15)

        # At least feat_2 should be identified as biased
        biased_names = [b["feature"] for b in result["biased_features"]]
        self.assertIn("feat_2", biased_names)


class TestLabelBias(unittest.TestCase):
    """Test label distribution bias detection."""

    def test_no_label_drift_identical_rates(self):
        """No drift for identical positive rates."""
        labels = [0, 0, 1, 1, 0, 1] * 10  # 50% positive rate

        result = detect_label_bias(labels, labels, bias_threshold=0.10)

        self.assertFalse(result["label_distribution_drift"])
        self.assertLess(result["rate_difference"], 0.10)

    def test_label_drift_detected(self):
        """Drift should be detected for different positive rates."""
        current = [0] * 80 + [1] * 20  # 20% positive
        reference = [0] * 50 + [1] * 50  # 50% positive

        result = detect_label_bias(current, reference, bias_threshold=0.10)

        self.assertTrue(result["label_distribution_drift"])
        self.assertGreater(result["rate_difference"], 0.20)

    def test_group_fairness_audit(self):
        """Should detect group fairness disparities."""
        labels = [0, 0, 1, 1] * 25  # 50% overall
        groups = {
            "group_a": list(range(0, 50)),  # Low positive rate (20%)
            "group_b": list(range(50, 100))  # High positive rate (80%)
        }

        current_labels = [0] * 40 + [1] * 10 + [1] * 40 + [0] * 10

        result = detect_label_bias(
            current_labels, current_labels, groups=groups)

        self.assertTrue(result["fairness_alert"])
        self.assertEqual(len(result["group_disparities"]), 2)


class TestRetrainTrigger(unittest.TestCase):
    """Test retrain trigger evaluation."""

    def test_no_retrain_needed(self):
        """No retrain if no governance signals."""
        drift = {"drift_detected": False, "drift_magnitude": 0.05}
        bias = {"bias_detected": False, "biased_features": []}
        label = {"label_distribution_drift": False, "fairness_alert": False}

        result = evaluate_retrain_trigger(drift, bias, label)

        self.assertFalse(result["retrain_required"])
        self.assertEqual(result["priority_level"], "NONE")
        self.assertEqual(result["recommendation"], "CONTINUE_MONITORING")

    def test_high_priority_retrain(self):
        """High priority for critical issues."""
        drift = {"drift_detected": True, "drift_magnitude": 0.25}
        bias = {"bias_detected": True, "biased_features": [{"feature": "f1"}]}
        label = {"label_distribution_drift": False, "fairness_alert": False}

        result = evaluate_retrain_trigger(drift, bias, label)

        self.assertTrue(result["retrain_required"])
        self.assertEqual(result["priority_level"], "CRITICAL")
        self.assertEqual(result["recommendation"], "IMMEDIATE_RETRAIN")

    def test_scheduled_retrain(self):
        """Scheduled retrain for medium-priority issues."""
        drift = {"drift_detected": False, "drift_magnitude": 0.05}
        bias = {"bias_detected": True, "biased_features": [{"feature": "f1"}]}
        label = {"label_distribution_drift": False, "fairness_alert": False}

        result = evaluate_retrain_trigger(drift, bias, label)

        self.assertTrue(result["retrain_required"])
        self.assertIn(result["priority_level"], ["HIGH", "MEDIUM"])


class TestExplainability(unittest.TestCase):
    """Test explainability metrics."""

    def test_explainability_scoring(self):
        """Explainability score should reflect feature concentration."""
        # Concentrated importance: 1 feature dominates
        importance_concentrated = {
            "feature_1": 0.8,
            "feature_2": 0.1,
            "feature_3": 0.05,
            "feature_4": 0.03,
            "feature_5": 0.02
        }

        result_concentrated = compute_explainability_metrics(
            [0.5] * 10, importance_concentrated)

        # Distributed importance
        importance_distributed = {
            f"feature_{i}": 1.0 for i in range(20)
        }

        result_distributed = compute_explainability_metrics(
            [0.5] * 10, importance_distributed)

        # Concentrated should have higher explainability (fewer top features needed)
        self.assertGreater(result_concentrated["explainability_score"],
                           result_distributed["explainability_score"])

    def test_top_features_extraction(self):
        """Should identify top features correctly."""
        importance = {
            "spend": 0.5,
            "ctr": 0.3,
            "impression": 0.1,
            "conversion": 0.08,
            "other": 0.02
        }

        result = compute_explainability_metrics([0.5] * 10, importance)

        top_5 = [f["feature"] for f in result["top_features"]]
        self.assertEqual(len(top_5), 5)
        self.assertEqual(top_5[0], "spend")  # Highest importance


class TestFullAudit(unittest.TestCase):
    """Test full ML governance audit."""

    def test_audit_execution(self):
        """Full audit should execute without errors."""
        result = run_ml_governance_audit(phase="all")

        # Check structure
        self.assertIn("audit_timestamp", result)
        self.assertIn("calibration_drift", result)
        self.assertIn("feature_bias", result)
        self.assertIn("label_bias", result)
        self.assertIn("retrain_trigger", result)
        self.assertIn("explainability_metrics", result)

        # Check values
        self.assertIsNotNone(result["retrain_trigger"]["recommendation"])
        self.assertIn(result["retrain_trigger"]["recommendation"],
                      ["IMMEDIATE_RETRAIN", "SCHEDULE_RETRAIN", "CONTINUE_MONITORING"])


if __name__ == "__main__":
    unittest.main()
