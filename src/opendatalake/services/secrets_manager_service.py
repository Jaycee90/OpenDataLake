
import json
import boto3


# Class responsible for retrieving database credentials from AWS Secrets Manager.
# This keeps AWS-specific credential retrieval separate from database configuration.
'''How it works
- Locally: Boto3 uses your configured AWS credentials.
- On ECS: Boto3 automatically uses the IAM task role.
- get_secret_value(): Retrieves the secret from AWS Secrets Manager.
- json.loads(): Converts the JSON secret into a Python dictionary.'''
class SecretsManagerService:
    def __init__(self, region_name: str = "us-east-1"):
        # Uses local AWS credentials or ECS task-role credentials.
        self.client = boto3.client(
            "secretsmanager",
            region_name=region_name,
        )

    def get_secret(self, secret_arn: str) -> dict:
        response = self.client.get_secret_value(
            SecretId=secret_arn
        )

        return json.loads(response["SecretString"])
