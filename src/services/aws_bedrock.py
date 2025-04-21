from botocore.exceptions import BotoCoreError, ClientError
import boto3
import json

class AWSBedrockService:
    def __init__(self, model_id, region_name='us-west-2'):
        self.model_id = model_id
        self.region_name = region_name
        self.client = boto3.client('bedrock-runtime', region_name=self.region_name)
        
    def get_model_response(self, prompt):
        """
        Get a response from the model based on the prompt
        """
        try:
            # Format the request body based on the model type
            if "anthropic" in self.model_id.lower():
                # Anthropic Claude models
                body = json.dumps({
                    "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                    "max_tokens_to_sample": 4000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                })
            elif "amazon.titan" in self.model_id.lower():
                # Amazon Titan models
                body = json.dumps({
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 4000,
                        "temperature": 0.7,
                        "topP": 0.9,
                    }
                })
            elif "meta.llama" in self.model_id.lower():
                # Meta Llama models
                body = json.dumps({
                    "prompt": prompt,
                    "max_gen_len": 4000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                })
            elif "cohere" in self.model_id.lower():
                # Cohere models
                body = json.dumps({
                    "prompt": prompt,
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "p": 0.9,
                })
            else:
                # Default format
                body = json.dumps({
                    "prompt": prompt,
                    "max_tokens": 4000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                })
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            
            # Extract the generated text based on the model type
            if "anthropic" in self.model_id.lower():
                return response_body.get('completion', '')
            elif "amazon.titan" in self.model_id.lower():
                return response_body.get('results', [{}])[0].get('outputText', '')
            elif "meta.llama" in self.model_id.lower():
                return response_body.get('generation', '')
            elif "cohere" in self.model_id.lower():
                return response_body.get('text', '')
            else:
                return str(response_body)
                
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return f"Error: {str(e)}"
    
    def list_available_models(self):
        """
        List all available models in AWS Bedrock
        """
        try:
            # Use bedrock client (not bedrock-runtime) for listing models
            bedrock_client = boto3.client('bedrock', region_name=self.region_name)
            response = bedrock_client.list_foundation_models()
            models = []
            
            for model in response.get('modelSummaries', []):
                model_id = model.get('modelId')
                provider = model.get('providerName')
                models.append({
                    'id': model_id,
                    'provider': provider,
                    'name': f"{provider} - {model_id}"
                })
                
            return models
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred listing models: {e}")
            return []
    def get_model_info(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return None
    def get_model_parameters(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelParameters', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_usage(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelUsage', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_status(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelStatus', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_metrics(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelMetrics', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_version(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelVersion', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_tags(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelTags', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_endpoint(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelEndpoint', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_endpoint_url(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelEndpointUrl', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_endpoint_status(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelEndpointStatus', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_endpoint_metrics(self):   
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelEndpointMetrics', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_endpoint_tags(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelEndpointTags', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_endpoint_version(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelEndpointVersion', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
    def get_model_endpoint_usage(self):
        try:
            response = self.client.describe_model(modelId=self.model_name)
            return response.get('modelEndpointUsage', {})
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return {}
 
