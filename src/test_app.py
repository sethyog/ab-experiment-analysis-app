import unittest
import os
import pandas as pd
from io import StringIO
from unittest.mock import Mock, patch
from app import app
from services.prompt_builder import PromptBuilder
from services.summary_generator import SummaryGenerator
from utils.file_handler import FileHandler
from services.aws_bedrock import AWSBedrockService

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

    # Add new test class for AWSBedrockService
    class TestAWSBedrockService(unittest.TestCase):
        def setUp(self):
            self.bedrock_service = AWSBedrockService('anthropic.claude-v2')

        @patch('boto3.client')
        def test_chunk_size_selection(self, mock_boto3):
            """Test that correct chunk sizes are selected for different models"""
            # Test for different model types
            models = {
                'anthropic.claude-v2': 1800,
                'amazon.titan': 1500,
                'meta.llama': 1500,
                'cohere.command': 1500,
                'unknown.model': 1000
            }
            
            for model_id, expected_size in models.items():
                service = AWSBedrockService(model_id)
                self.assertEqual(service._get_chunk_size(), expected_size)

        def test_split_into_chunks(self):
            """Test the chunk splitting functionality"""
            # Create a long text with known sentence boundaries
            long_text = "This is sentence one. This is sentence two. " * 50
            chunk_size = 100
            
            chunks = self.bedrock_service._split_into_chunks(long_text, chunk_size)
            
            # Verify each chunk
            for chunk in chunks:
                self.assertLessEqual(len(chunk), chunk_size)
                # Verify chunks end with complete sentences
                self.assertTrue(chunk.endswith('.') or chunk.endswith('!') or chunk.endswith('?'))

        @patch('boto3.client')
        def test_process_chunk(self, mock_boto3):
            """Test processing of individual chunks"""
            # Mock the AWS response
            mock_response = {
                'body': Mock(read=lambda: json.dumps({'completion': 'Test response'}))
            }
            mock_boto3.return_value.invoke_model.return_value = mock_response
            
            response = self.bedrock_service._process_chunk("Test prompt")
            self.assertEqual(response, 'Test response')

        @patch('boto3.client')
        def test_get_model_response(self, mock_boto3):
            """Test the complete response generation process"""
            # Mock the AWS response
            mock_response = {
                'body': Mock(read=lambda: json.dumps({'completion': 'Test response'}))
            }
            mock_boto3.return_value.invoke_model.return_value = mock_response
            
            # Test with a long prompt
            long_prompt = "Test prompt. " * 1000
            response = self.bedrock_service.get_model_response(long_prompt)
            
            # Verify the response
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)

        @patch('boto3.client')
        def test_streaming_response(self, mock_boto3):
            """Test the streaming response functionality"""
            # Mock the AWS response
            mock_response = {
                'body': Mock(read=lambda: json.dumps({'completion': 'Test response'}))
            }
            mock_boto3.return_value.invoke_model.return_value = mock_response
            
            # Test with a long prompt
            long_prompt = "Test prompt. " * 1000
            responses = list(self.bedrock_service.get_model_response_streaming(long_prompt))
            
            # Verify we got multiple chunks
            self.assertTrue(len(responses) > 0)
            for response in responses:
                self.assertIsInstance(response, str)

        def test_error_handling(self):
            """Test error handling in the service"""
            # Test with invalid model ID
            with self.assertRaises(Exception):
                AWSBedrockService('invalid.model')
            
            # Test with empty prompt
            response = self.bedrock_service.get_model_response("")
            self.assertTrue("Error" in response)

    # Existing tests...
    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'A/B Experiment Analysis', response.data)
    
    def test_prompt_builder(self):
        prompt_builder = PromptBuilder()
        df = pd.read_csv(StringIO(self.test_csv_data))
        prompt = prompt_builder.build_prompt("Focus on conversion rate", df)
        
        self.assertIn("Focus on conversion rate", prompt)
        self.assertIn("conversion_rate", prompt)
        self.assertIn("0.12", prompt)
        self.assertIn("0.15", prompt)
    
    def test_summary_generator(self):
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
        
        self.assertEqual(result['summary'], "The A/B test shows a statistically significant improvement in conversion rate and average order value.")
        self.assertEqual(len(result['key_metrics']), 1)
        self.assertEqual(result['key_metrics'][0]['metric_name'], "Conversion Rate")
        self.assertEqual(len(result['recommendations']), 2)
        self.assertEqual(result['recommendations'][0], "Implement the treatment version")
    
    def test_file_handler(self):
        file_handler = FileHandler(upload_folder='test_uploads')
        
        df = file_handler.read_csv('test_uploads/test.csv')
        self.assertEqual(len(df), 3)
        self.assertEqual(len(df.columns), 5)
        
        self.assertTrue(file_handler.validate_csv_content(df))

if __name__ == '__main__':
    unittest.main()
