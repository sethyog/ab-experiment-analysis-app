import unittest
import os
import pandas as pd
import json
from io import StringIO
from unittest.mock import Mock, patch
from src.app import app
from src.services.prompt_builder import PromptBuilder
from src.services.summary_generator import SummaryGenerator
from src.utils.file_handler import FileHandler
from src.services.aws_bedrock import AWSBedrockService
from src.services.example_manager import ExampleManager

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
        
        # Test without field descriptions or examples
        prompt = prompt_builder.build_prompt("Focus on conversion rate", df)
        self.assertIn("Focus on conversion rate", prompt)
        self.assertIn("conversion_rate", prompt)
        self.assertIn("0.12", prompt)
        self.assertIn("0.15", prompt)
        self.assertNotIn("## FIELD DESCRIPTIONS:", prompt)
        self.assertNotIn("## EXAMPLES OF GOOD ANALYSES:", prompt)
        
        # Test with field descriptions
        field_descriptions = {
            "conversion_rate": "The percentage of users who completed a desired action",
            "p_value": "The probability that the observed difference occurred by chance"
        }
        prompt_with_desc = prompt_builder.build_prompt("Focus on conversion rate", df, field_descriptions)
        self.assertIn("## FIELD DESCRIPTIONS:", prompt_with_desc)
        self.assertIn("conversion_rate: The percentage of users who completed a desired action", prompt_with_desc)
        self.assertIn("p_value: The probability that the observed difference occurred by chance", prompt_with_desc)
        
        # Test with examples
        example = {
            'metadata': {'name': 'Test Example'},
            'data': df,
            'analysis': {
                'summary': 'Example summary',
                'key_metrics': [{'metric_name': 'Test Metric', 'value': 'Test Value', 'interpretation': 'Test Interpretation'}]
            }
        }
        prompt_with_examples = prompt_builder.build_prompt("Focus on conversion rate", df, examples=[example])
        self.assertIn("## EXAMPLES OF GOOD ANALYSES:", prompt_with_examples)
        self.assertIn("### EXAMPLE: Test Example", prompt_with_examples)
        self.assertIn("Example summary", prompt_with_examples)
        
        # Test with both field descriptions and examples
        prompt_with_both = prompt_builder.build_prompt("Focus on conversion rate", df, field_descriptions, [example])
        self.assertIn("## FIELD DESCRIPTIONS:", prompt_with_both)
        self.assertIn("## EXAMPLES OF GOOD ANALYSES:", prompt_with_both)
    
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
        
        # Test field descriptions functionality with field_name,description format
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("field_name,description\n")
            temp_file.write("conversion_rate,The percentage of users who completed a desired action\n")
            temp_file.write("p_value,The probability that the observed difference occurred by chance\n")
            temp_path_1 = temp_file.name
            
        # Test field descriptions functionality with Column,Description format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("Column,Description\n")
            temp_file.write("conversion_rate,The percentage of users who completed a desired action\n")
            temp_file.write("p_value,The probability that the observed difference occurred by chance\n")
            temp_path_2 = temp_file.name
            
        # Test field descriptions functionality with custom column names
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write("FieldName,FieldDescription\n")
            temp_file.write("conversion_rate,The percentage of users who completed a desired action\n")
            temp_file.write("p_value,The probability that the observed difference occurred by chance\n")
            temp_path_3 = temp_file.name
            
        try:
            # Test with field_name,description format
            file_handler_with_desc_1 = FileHandler(upload_folder='test_uploads', descriptions_path=temp_path_1)
            descriptions_1 = file_handler_with_desc_1.get_field_descriptions(df)
            self.assertIn('conversion_rate', descriptions_1)
            self.assertEqual(descriptions_1['conversion_rate'], 'The percentage of users who completed a desired action')
            self.assertIn('p_value', descriptions_1)
            self.assertEqual(descriptions_1['p_value'], 'The probability that the observed difference occurred by chance')
            
            # Test with Column,Description format
            file_handler_with_desc_2 = FileHandler(upload_folder='test_uploads', descriptions_path=temp_path_2)
            descriptions_2 = file_handler_with_desc_2.get_field_descriptions(df)
            self.assertIn('conversion_rate', descriptions_2)
            self.assertEqual(descriptions_2['conversion_rate'], 'The percentage of users who completed a desired action')
            self.assertIn('p_value', descriptions_2)
            self.assertEqual(descriptions_2['p_value'], 'The probability that the observed difference occurred by chance')
            
            # Test with custom column names
            file_handler_with_desc_3 = FileHandler(upload_folder='test_uploads', descriptions_path=temp_path_3)
            descriptions_3 = file_handler_with_desc_3.get_field_descriptions(df)
            self.assertIn('conversion_rate', descriptions_3)
            self.assertEqual(descriptions_3['conversion_rate'], 'The percentage of users who completed a desired action')
            self.assertIn('p_value', descriptions_3)
            self.assertEqual(descriptions_3['p_value'], 'The probability that the observed difference occurred by chance')
        finally:
            # Clean up the temporary files
            import os
            if os.path.exists(temp_path_1):
                os.remove(temp_path_1)
            if os.path.exists(temp_path_2):
                os.remove(temp_path_2)
            if os.path.exists(temp_path_3):
                os.remove(temp_path_3)

    def test_example_manager(self):
        """Test the ExampleManager functionality"""
        # Create a temporary example directory structure
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        data_dir = os.path.join(temp_dir, 'data')
        analyses_dir = os.path.join(temp_dir, 'analyses')
        os.makedirs(data_dir)
        os.makedirs(analyses_dir)
        
        # Create test metadata
        metadata = {
            "examples": [
                {
                    "id": "test1",
                    "name": "Test Example 1",
                    "data_file": "test1.csv",
                    "analysis_file": "test1.json",
                    "description": "Test example 1",
                    "tags": ["test", "conversion"],
                    "metrics": ["conversion_rate", "bounce_rate"]
                },
                {
                    "id": "test2",
                    "name": "Test Example 2",
                    "data_file": "test2.csv",
                    "analysis_file": "test2.json",
                    "description": "Test example 2",
                    "tags": ["test", "revenue"],
                    "metrics": ["average_order_value", "revenue"]
                }
            ]
        }
        
        with open(os.path.join(temp_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Create test data files
        with open(os.path.join(data_dir, 'test1.csv'), 'w') as f:
            f.write("""metric,control,treatment,difference,p_value
conversion_rate,0.12,0.15,0.03,0.04
bounce_rate,0.35,0.32,-0.03,0.06
""")
        
        with open(os.path.join(data_dir, 'test2.csv'), 'w') as f:
            f.write("""metric,control,treatment,difference,p_value
average_order_value,45.5,48.2,2.7,0.03
revenue,1000,1200,200,0.02
""")
        
        # Create test analysis files
        with open(os.path.join(analyses_dir, 'test1.json'), 'w') as f:
            json.dump({
                "summary": "Test summary 1",
                "key_metrics": [{"metric_name": "Conversion Rate", "value": "0.15", "interpretation": "Good"}]
            }, f)
        
        with open(os.path.join(analyses_dir, 'test2.json'), 'w') as f:
            json.dump({
                "summary": "Test summary 2",
                "key_metrics": [{"metric_name": "Average Order Value", "value": "48.2", "interpretation": "Good"}]
            }, f)
        
        try:
            # Initialize the example manager with the temp directory
            example_manager = ExampleManager(examples_dir=temp_dir)
            
            # Test loading metadata
            examples = example_manager.get_all_examples()
            self.assertEqual(len(examples), 2)
            self.assertEqual(examples[0]['id'], 'test1')
            self.assertEqual(examples[1]['id'], 'test2')
            
            # Test getting example data
            data1 = example_manager.get_example_data('test1')
            self.assertIsInstance(data1, pd.DataFrame)
            self.assertEqual(len(data1), 2)
            self.assertIn('conversion_rate', data1['metric'].values)
            
            # Test getting example analysis
            analysis1 = example_manager.get_example_analysis('test1')
            self.assertEqual(analysis1['summary'], 'Test summary 1')
            
            # Test selecting examples based on input data
            test_df = pd.DataFrame({
                'metric': ['conversion_rate', 'bounce_rate', 'time_on_site'],
                'control': [0.1, 0.3, 100],
                'treatment': [0.12, 0.28, 110],
                'difference': [0.02, -0.02, 10],
                'p_value': [0.03, 0.04, 0.02]
            })
            
            selected = example_manager.select_examples(test_df, max_examples=1)
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]['metadata']['id'], 'test1')  # Should select test1 due to metric overlap
            
            # Test random example selection
            random_examples = example_manager.get_random_examples(max_examples=1)
            self.assertEqual(len(random_examples), 1)
            self.assertIn(random_examples[0]['metadata']['id'], ['test1', 'test2'])
            
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main()


