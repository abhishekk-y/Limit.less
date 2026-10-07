import unittest
from datetime import datetime, timedelta
from packages.scoring.shi.calculator import SHICalculator

class TestSHI(unittest.TestCase):
    def test_moderate_growth_emerging(self):
        """10% monthly growth -> k≈0.095 -> 'emerging' (k>0.02 but <0.1)"""
        calc = SHICalculator()
        now = datetime.now()
        data = [(now + timedelta(days=30*i), int(100 * (1.1 ** i))) for i in range(10)]
        res = calc.compute("docker", data)
        self.assertTrue(res.k > 0)
        self.assertEqual(res.trend_class, "emerging")
        self.assertGreater(res.r2, 0.8)

    def test_explosive_growth(self):
        """20% monthly growth -> k≈0.18 -> 'exploding' (k>0.1)"""
        calc = SHICalculator()
        now = datetime.now()
        data = [(now + timedelta(days=30*i), int(100 * (1.2 ** i))) for i in range(10)]
        res = calc.compute("rag", data)
        self.assertTrue(res.k > 0.1)
        self.assertEqual(res.trend_class, "exploding")

    def test_decay(self):
        """Negative growth -> decay/cooling"""
        calc = SHICalculator()
        now = datetime.now()
        data = [(now + timedelta(days=30*i), int(1000 * (0.85 ** i))) for i in range(10)]
        res = calc.compute("jquery", data)
        self.assertTrue(res.k < 0)
        self.assertIn(res.trend_class, ["decaying", "cooling"])

    def test_insufficient_data(self):
        """Too few data points should raise ValueError"""
        calc = SHICalculator(min_data_points=6)
        now = datetime.now()
        data = [(now + timedelta(days=30*i), 100) for i in range(3)]
        with self.assertRaises(ValueError):
            calc.compute("sparse_skill", data)

    def test_doubling_time_positive(self):
        """Doubling time should be positive and finite for growing skills"""
        calc = SHICalculator()
        now = datetime.now()
        data = [(now + timedelta(days=30*i), int(100 * (1.1 ** i))) for i in range(10)]
        res = calc.compute("python", data)
        self.assertTrue(0 < res.half_life_or_doubling < 100)

if __name__ == "__main__":
    unittest.main()
