import copy
import unittest

from benchmarks.render_breadth import JSON, MODELS, selected


class ComparisonSelectionTests(unittest.TestCase):
    def setUp(self):
        self.results: JSON = {
            "campaigns": [
                {
                    "trials": [
                        {
                            "requestedModel": model,
                            "case": "one",
                            "exception": None,
                            "reward": 1,
                        }
                        for model in MODELS
                    ]
                }
            ]
        }

    def test_setup_retry_is_distinct_from_best_of_predictions(self):
        failed = copy.deepcopy(self.results["campaigns"][0]["trials"][0])
        failed["exception"] = "SetupError"
        failed["reward"] = None
        self.results["campaigns"].append({"trials": [failed]})
        self.assertEqual(len(selected(self.results, {"one"})), 2)
        duplicate = copy.deepcopy(failed)
        duplicate["exception"] = None
        duplicate["reward"] = 0
        self.results["campaigns"].append({"trials": [duplicate]})
        with self.assertRaisesRegex(ValueError, "Multiple graded"):
            selected(self.results, {"one"})

    def test_incomplete_model_arm_cannot_be_published_as_paired(self):
        self.results["campaigns"][0]["trials"].pop()
        with self.assertRaisesRegex(ValueError, "every case"):
            selected(self.results, {"one"})
