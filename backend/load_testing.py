from locust import task, FastHttpUser, HttpUser
import json
import uuid
import random


class MyUser(HttpUser):

    @task
    def async_task_executor(self):
        self.user_id = str(uuid.uuid4())

        self.client.post(
            "/api/v1/job_executor/async?executor=standard",
            json={
                "job_name": "Preformence Test Job",
                "user_id": self.user_id,
                "description": "",
                "estimated_time": random.randrange(20, 60)
            }
        )