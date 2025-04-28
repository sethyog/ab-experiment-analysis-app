from flask import Flask, request, render_template, flash
import os
import traceback
from src.services.aws_bedrock import AWSBedrockService
from src.services.prompt_builder import PromptBuilder
from src.services.summary_generator import SummaryGenerator
from src.services.example_manager import ExampleManager
from src.utils.file_handler import FileHandler

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages

# Initialize services
file_handler = FileHandler(upload_folder='uploads')
prompt_builder = PromptBuilder()
summary_generator = SummaryGenerator()
example_manager = ExampleManager(examples_dir='src/examples')

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route for the application
    """
    result = None
    error = None
    
    if request.method == 'POST':
        try:
            # Get form data
            csv_file = request.files.get('csv_file')
            instructions = request.form.get('instructions', '')
            model_name = request.form.get('model_name')
            use_examples = request.form.get('use_examples', 'on') == 'on'
            
            # Validate inputs
            if not csv_file:
                raise ValueError("No CSV file provided")
                
            if not model_name:
                raise ValueError("No model selected")
            
            # Process the CSV file
            file_path = file_handler.save_file(csv_file)
            print(f"File saved to {file_path}")
            data_df = file_handler.read_csv(file_path)
            file_handler.validate_csv_content(data_df)
            
            # Get field descriptions
            field_descriptions = file_handler.get_field_descriptions(data_df)
            
            # Get examples if enabled
            examples = []
            if use_examples:
                examples = example_manager.select_examples(data_df, max_examples=2)
                print(f"Selected {len(examples)} examples for few-shot learning")
            
            # Build the prompt
            prompt = prompt_builder.build_prompt(instructions, data_df, field_descriptions, examples)
            print(f"Prompt: {prompt}")
            
            # Get response from AWS Bedrock
            bedrock_service = AWSBedrockService(model_id=model_name)
            model_response = bedrock_service.get_model_response(prompt)
            
            # Generate summary
            result = summary_generator.generate_summary(model_response)
            
        except Exception as e:
            error = str(e)
            print(f"Error: {error}")
            print(traceback.format_exc())
    
    # Get available models for the dropdown
    try:
        # Use a default model ID for initialization
        bedrock_service = AWSBedrockService(model_id="anthropic.claude-v2")
        available_models = bedrock_service.list_available_models()
    except Exception as e:
        print(f"Error fetching models: {e}")
        available_models = []
    
    return render_template('index.html', result=result, error=error, models=available_models)

@app.route('/models', methods=['GET'])
def get_models():
    """
    Route to get available models
    """
    try:
        # Use a default model ID for initialization
        bedrock_service = AWSBedrockService(model_id="anthropic.claude-v2")
        models = bedrock_service.list_available_models()
        return {'models': models}
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
