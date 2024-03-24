from pydantic import BaseSettings, PostgresDsn
from typing import Dict, Any


class Settings(BaseSettings):

    DATA_SERVICE_URL: str

    MAX_LAMBDA_CONCURRENCY: int = 10
    MESSAGING_QUEUE_PROVIDER: str = "AWS"

    AWS_SQS_SOLUTIONS_QUEUE_URL: str = ""
    AWS_SQS_SOLUTIONS_QUEUE_MAX_RETRIES: int = 5
    AWS_SQS_SOLUTIONS_QUEUE_REGION: str = "us-east-1"

    STANDARD_QUEUE_NAME: str="test"
    STANDARD_QUEUE_WORKERS: int = 2



settings = Settings()
