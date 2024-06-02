from abc import ABC, abstractmethod
import boto3
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
import json
from typing import Protocol, List
import time
import requests
import os

class WorkerProtocol(Protocol):
    def start(self):
        ...

    def stop(self):
        ...


class Worker(ABC):
    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...


class StandardQueueWorker(Worker):
    def __init__(self, queue_name: str):
        self.stop_listening = False
        self.queue_name = queue_name

    def start(self):
        sqs_client = boto3.client("sqs")

        #Get the URL of the SQS queue
        response = sqs_client.get_queue_url(QueueName=self.queue_name)
        sqs_queue_url = response["QueueUrl"]
        logger.info(f"sqs_queue_url: {sqs_queue_url}")

        while not self.stop_listening:
            try:
                #Receive messages from the SQS queue
                response = sqs_client.receive_message(
                    QueueUrl=sqs_queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=20,  #Long polling - wait up to 20 seconds for a message
                )
                if "Messages" in response:
                    for msg in response["Messages"]:
                        message_body = msg["Body"]
                        receipt_handle = msg["ReceiptHandle"]
                        logger.info(f"Received message_body: {message_body}")
                        payload = json.loads(message_body).get("payload")
                        estimated_time = payload.get("estimated_time")
                        job_id = payload.get("job_id")
                        url = f"{os.environ['DATA_SERVICE_URL']}/job/{job_id}"

                        try:
                            
                            requests.put(url=url,json={"status":"running"})
                            time.sleep(estimated_time)
                            requests.put(url=url,json={"status":"completed"})
                            logger.info(
                                f"Execution of Job Completed!!!"
                            )
                        except Exception as e:
                            logger.exception("Error while Execution of Job: %s", e)
                            requests.put(url=url,json={"status":"failed"})

                        logger.info("Deleting the message from queue")
                        sqs_client.delete_message(
                            QueueUrl=sqs_queue_url, ReceiptHandle=receipt_handle
                        )
            except Exception as e:
                logger.exception("Error while receiving messages from SQS: %s", e)

    def stop(self):
        self.stop_listening = True


class WorkerExecutor:
    def __init__(
        self,
        worker: WorkerProtocol,
        max_workers: int = 2,
    ):
        self.worker: WorkerProtocol = worker
        self.workers = []
        self.thread_pool_executor = None
        self.submit_futures = []
        self.max_workers = max_workers

    def start(self):
        logger.info("Starting all workers")

        self.thread_pool_executor = ThreadPoolExecutor(max_workers=self.max_workers)

        for i in range(0, self.max_workers):
            self.workers.append(self.worker)
        for worker in self.workers:
            self.submit_futures.append(self.thread_pool_executor.submit(worker.start))

        logger.info("Started all workers....")

    def stop(self):
        logger.warning("Handling application shutdown")
        for worker in self.workers:
            worker.stop()
        self.thread_pool_executor.shutdown(wait=True)
        logger.info("Shutdown completed")


class WorkerExecutorManager:
    _instance = None

    def __new__(cls, workers: List[WorkerExecutor] = []):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.workers = workers
        return cls._instance

    def start_workers(self):
        for we in self.workers:
            we.start()

    def stop_workers(self):
        for we in self.workers:
            we.stop()


if __name__=="__main__":
    import signal
    import os
    def handle_signal(signum, frame):
        logger.info(f"Received signal {signum}, stopping workers...")
        standard_executor.stop()
        exit(0)
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    standard_executor = WorkerExecutor(
    worker=StandardQueueWorker(queue_name=os.environ["STANDARD_QUEUE_NAME"]),
    max_workers=int(os.environ["STANDARD_QUEUE_WORKERS"]))
    standard_executor.start()
    signal.pause() 
    