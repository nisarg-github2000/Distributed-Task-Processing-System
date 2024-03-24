import traceback
from datetime import datetime
from loguru import logger
from main import settings
import json
from aiobotocore.session import get_session


async def send_message(
    queue_name: str, payload: dict, job_id:str,**kwargs
):
    message_body = {
        "version": kwargs.get("version", "1.0"),
        "message_timestamp": str(datetime.utcnow()),
    }
    payload["job_id"]=job_id
    message_body["payload"] = payload
    logger.info(f"message: {message_body}")

    try:
        session = get_session()
        async with session.create_client("sqs",region_name='us-east-1') as sqs_client:
            response = await sqs_client.get_queue_url(QueueName="test")
            sqs_queue_url = response["QueueUrl"]
            logger.info(
                f"sending message to queue url {sqs_queue_url} with message body {message_body}"
            )
            response = await sqs_client.send_message(
                QueueUrl=sqs_queue_url,
                MessageBody=json.dumps(message_body),
            )
        logger.info(f"Sent Message with Message ID: {response['MessageId']}")
    except Exception as ex:
        logger.info("Error in sending Message to the queue", ex)
        traceback.print_exc()