import unittest
import os
from unittest.mock import patch, MagicMock

# Assuming the ReportGenerator class is in src/helpers/report_generator.py
from src.helpers.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):

    def test_report_generator_init(self):
        # Since the __init__ is currently empty, a basic instantiation test is sufficient.
        # If functionality is added later, more specific tests will be needed.
        try:
            generator = ReportGenerator()
            self.assertIsInstance(generator, ReportGenerator)
        except Exception as e:
            self.fail(f"ReportGenerator instantiation failed: {e}")

if __name__ == '__main__':
    unittest.main()
