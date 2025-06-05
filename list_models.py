# Bedrock 모델 목록 조회 -> 잘 연결되어있는 지 확인용이였음 
import boto3
import os

client = boto3.client(
    service_name='bedrock',
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

response = client.list_foundation_models()
for model in response['modelSummaries']:
    print(model['modelId'])
