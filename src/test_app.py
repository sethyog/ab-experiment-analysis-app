import unittest
import os
import pandas as pd
from io import StringIO
from app import app
from services.prompt_builder import PromptBuilder
from services.summary_generator import SummaryGenerator
from utils.file_handler import FileHandler

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        # Create test data
        self.test_csv_data = """metric,control,treatment,difference,p_value
conversion_rate,0.12,0.15,0.03,0.04
average_order_value,45.5,48.2,2.7,0.03
bounce_rate,0.35,0.32,-0.03,0.06
"""
        # Create a test file
        os.makedirs('test_uploads', exist_ok=True)
        with open('test_uploads/test.csv', 'w') as f:
            f.write(self.test_csv_data)
            
    def tearDown(self):
        # Clean up test files
        if os.path.exists('test_uploads/test.csv'):
            os.remove('test_uploads/test.csv')
        if os.path.exists('test_uploads'):
            os.rmdir('test_uploads')
    
    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'A/B Experiment Analysis', response.data)
    
    def test_prompt_builder(self):
        # Test the prompt builder
        prompt_builder = PromptBuilder()
        df = pd.read_csv(StringIO(self.test_csv_data))
        prompt = prompt_builder.build_prompt("Focus on conversion rate", df)
        
        # Check that the prompt contains the expected elements
        self.assertIn("Focus on conversion rate", prompt)
        self.assertIn("conversion_rate", prompt)
        self.assertIn("0.12", prompt)  # Control value
        self.assertIn("0.15", prompt)  # Treatment value
    
    def test_summary_generator(self):
        # Test the summary generator with a mock response
        summary_generator = SummaryGenerator()
        mock_response = """```json
{
  "summary": "The A/B test shows a statistically significant improvement in conversion rate and average order value.",
  "key_metrics": [
    {
      "metric_name": "Conversion Rate",
      "value": "+0.03 (25% increase)",
      "interpretation": "Statistically significant improvement (p=0.04)"
    }
  ],
  "statistical_significance": "Two metrics show statistical significance at p<0.05",
  "recommendations": [
    "Implement the treatment version",
    "Monitor bounce rate after implementation"
  ],
  "limitations": [
    "Short test duration may not account for seasonal effects"
  ]
}
```"""
        
        result = summary_generator.generate_summary(mock_response)
        
        # Check that the result contains the expected elements
        self.assertEqual(result['summary'], "The A/B test shows a statistically significant improvement in conversion rate and average order value.")
        self.assertEqual(len(result['key_metrics']), 1)
        self.assertEqual(result['key_metrics'][0]['metric_name'], "Conversion Rate")
        self.assertEqual(len(result['recommendations']), 2)
        self.assertEqual(result['recommendations'][0], "Implement the treatment version")
    
    def test_file_handler(self):
        # Test the file handler
        file_handler = FileHandler(upload_folder='test_uploads')
        
        # Test reading a CSV file
        df = file_handler.read_csv('test_uploads/test.csv')
        self.assertEqual(len(df), 3)  # 3 rows
        self.assertEqual(len(df.columns), 5)  # 5 columns
        
        # Test validation
        self.assertTrue(file_handler.validate_csv_content(df))

if __name__ == '__main__':
    unittest.main()