import unittest
from analytics_engine import UPIAnalyticsEngine
import pandas as pd

class TestUPIAnalytics(unittest.TestCase):
    def setUp(self):
        self.engine = UPIAnalyticsEngine()

    def test_cagr_calculation(self):
        cagr = self.engine.get_cagr()
        self.assertGreater(cagr, 0)

    def test_volume_scale(self):
        # Latest volume should be ~1.4B = 140,000 Lakhs
        self.assertGreater(self.engine.df['UPI_Volume_Lakhs'].iloc[-1], 130000)

if __name__ == '__main__':
    unittest.main()
