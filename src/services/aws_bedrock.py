from botocore.exceptions import BotoCoreError, ClientError
import boto3
import json

class AWSBedrockService:
    def __init__(self, model_name, region_name='us-east-1'):
        self.model_name = model_name
        self.region_name = region_name
        self.client = boto3.client('bedrock', region_name=self.region_name)

    def authenticate(self):
        # Authentication is handled by boto3 using environment variables or AWS config
        pass

    def generate_summary(self, prompt):
        try:
            response = self.client.invoke_model(
                modelId=self.model_name,
                body=json.dumps({"input": prompt}),
                contentType='application/json'
            )
            return json.loads(response['body'].read())
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return None

    def list_models(self):
        try:
            response = self.client.list_models()
            return response.get('modelSummaries', [])
        except (BotoCoreError, ClientError) as e:
            print(f"An error occurred: {e}")
            return []