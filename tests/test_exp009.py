import unittest

from lifelike_min.exp009_evaluation import run


class Exp009DevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run()

    def test_developer_gate(self):
        self.assertTrue(self.report["developer_gate"], self.report["failures"])

    def test_each_section(self):
        for name, row in self.report["sections"].items():
            with self.subTest(section=name):
                self.assertTrue(row["passed"], row)

    def test_zero_new_state_claim(self):
        self.assertEqual(self.report["new_persistent_fields"], 0)
        self.assertEqual(self.report["new_counted_mechanisms"], 0)


if __name__ == "__main__":
    unittest.main()
