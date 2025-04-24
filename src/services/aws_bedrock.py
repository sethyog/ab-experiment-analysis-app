from botocore.exceptions import BotoCoreError, ClientError
import boto3
import json
from typing import List
import re

class AWSBedrockService:
    '''
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
    '''
    def __init__(self, model_id, region_name='us-west-2'):
        self.model_id = model_id
        self.region_name = region_name
        self.client = boto3.client('bedrock-runtime', region_name=self.region_name)
        # Define model-specific chunk sizes
        self.chunk_sizes = {
            'anthropic': 1800,
            'amazon.titan': 1500,
            'meta.llama': 1500,
            'cohere': 1500,
            'default': 1000
        }

    def _get_chunk_size(self) -> int:
        """Get the appropriate chunk size based on the model"""
        for model_type, size in self.chunk_sizes.items():
            if model_type in self.model_id.lower():
                return size
        return self.chunk_sizes['default']

    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks intelligently at sentence boundaries
        """
        # Split text into sentences
        sentences = re.split('([.!?]+[\s\n]+)', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _process_chunk(self, chunk: str) -> str:
        """Process a single chunk using the model"""
        print(f'Processing chunk with model {self.model_id.lower()}')
        try:
            if "anthropic" in self.model_id.lower():
                body = json.dumps({
                    "prompt": f"\n\nHuman: {chunk}\n\nAssistant:",
                    "max_tokens_to_sample": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9,
                })
            elif "amazon.titan" in self.model_id.lower():
                body = json.dumps({
                    "inputText": chunk,
                    "textGenerationConfig": {
                        "maxTokenCount": 2048,
                        "temperature": 0.7,
                        "topP": 0.9,
                    }
                })
            elif "meta.llama" in self.model_id.lower():
                body = json.dumps({
                    "prompt": chunk,
                    "max_gen_len": 2048,
                    "temperature": 0.7,
                    "top_p": 0.9,
                })
            elif "cohere" in self.model_id.lower():
                body = json.dumps({
                    "prompt": chunk,
                    "max_tokens": 2048,
                    "temperature": 0.7,
                    "p": 0.9,
                })
            else:
                body = json.dumps({
                    "prompt": chunk,
                    "max_tokens": 2048,
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

            # Extract response based on model type
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
            return f"Error processing chunk: {str(e)}"

    def get_model_response(self, prompt: str) -> str:
        """
        Process the input prompt by breaking it into chunks and combining the responses
        """
        try:
            print('Get appropriate chunk size for the model')
            chunk_size = self._get_chunk_size()

            # Split the prompt into chunks
            chunks = self._split_into_chunks(prompt, chunk_size)

            # Process each chunk and collect responses
            responses = []
            for i, chunk in enumerate(chunks):
                # Add context for continuation chunks
                if i > 0:
                    chunk = f"Continuing from previous part: {chunk}"
                
                response = self._process_chunk(chunk)
                responses.append(response)

            # Combine responses
            combined_response = " ".join(responses)
            
            return combined_response

        except Exception as e:
            return f"Error: {str(e)}"

    def get_model_response_streaming(self, prompt: str):
        """
        Generator function to stream responses chunk by chunk
        """
        try:
            chunk_size = self._get_chunk_size()
            chunks = self._split_into_chunks(prompt, chunk_size)

            for i, chunk in enumerate(chunks):
                if i > 0:
                    chunk = f"Continuing from previous part: {chunk}"
                
                response = self._process_chunk(chunk)
                yield response

        except Exception as e:
            yield f"Error: {str(e)}"


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
 
