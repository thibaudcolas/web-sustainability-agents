import copy
import unittest

from benchmarks.render_scope import MODELS, selected


class ScopeComparisonSelectionTests(unittest.TestCase):
    def setUp(self):
        self.results = {
            "campaigns": [
                {
                    "trials": [
                        {
                            "requestedModel": model,
                            "requestedReasoning": "high",
                            "case": "case",
                            "exception": None,
                            "reward": 1,
                        }
                        for model in MODELS
                    ]
                }
            ]
        }

    def test_same_inputs_need_one_high_reasoning_prediction_per_arm(self):
        self.assertEqual(len(selected(self.results, {"case"})), 2)
        wrong_reasoning = copy.deepcopy(self.results)
        wrong_reasoning["campaigns"][0]["trials"][0]["requestedReasoning"] = "low"
        with self.assertRaisesRegex(ValueError, "high reasoning"):
            selected(wrong_reasoning, {"case"})
        self.results["campaigns"][0]["trials"].pop()
        with self.assertRaisesRegex(ValueError, "every case"):
            selected(self.results, {"case"})

    def test_setup_retries_do_not_allow_best_of_graded_predictions(self):
        retry = copy.deepcopy(self.results["campaigns"][0]["trials"][0])
        retry["exception"] = "SetupError"
        retry["reward"] = None
        self.results["campaigns"].append({"trials": [retry]})
        self.assertEqual(len(selected(self.results, {"case"})), 2)
        retry["exception"] = None
        retry["reward"] = 0
        with self.assertRaisesRegex(ValueError, "Multiple graded"):
            selected(self.results, {"case"})
