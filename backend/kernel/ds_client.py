# from aiohttp import ClientSession, ClientTimeout
# from loguru import logger
# from dataclasses import dataclass
# from typing import Optional, Any
# from uuid import UUID, uuid4

# @dataclass
# class DataServiceClient:
#     DATASERVICE_BASE_URL: str
#     @property
#     def headers(self) -> dict:
#         return {}

#     async def create_empty_job(
#         self,client: ClientSession, description:str, estimated_time:float,job_name:str,user_id:str
#     ) -> str:
#         payload = {
#             "id":str(uuid4()),
#             "description": description,
#             "estimated_time": estimated_time,
#             "status": "unknown",
#             "name": job_name,
#             "user_id": user_id
#         }
#         url = f"{self.DATASERVICE_BASE_URL}/job/"
#         async with client.post(url=url, json=payload, headers=self.headers) as resp:
#             resp_json = await resp.json()
#             logger.info(f"{resp_json=}")
#             return str(resp_json["id"])
        
#     async def update_job(self,client: ClientSession,job_id:str,payload:Optional[Any])->Optional[Any]:
#       url = f"{self.DATASERVICE_BASE_URL}/job/{job_id}"
#       async with client.put(url=url, json=payload, headers=self.headers) as resp:
#             resp_json = await resp.json()
#             logger.info(f"{resp_json=}")
#             return resp_json

import asyncio
from aiohttp import ClientSession, ClientTimeout
from loguru import logger
from dataclasses import dataclass
from typing import Optional, Any
from uuid import UUID, uuid4

@dataclass
class DataServiceClient:
    DATASERVICE_BASE_URL: str

    @property
    def headers(self) -> dict:
        return {"Content-Type": "application/json"}

    async def _request_with_retry(self, method: str, url: str, payload: Optional[Any] = None, retries: int = 5, timeout: float = 10.0):
        timeout = ClientTimeout(total=timeout)
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=timeout) as session:
                    if method.lower() == 'post':
                        response = await session.post(url, json=payload, headers=self.headers)
                    elif method.lower() == 'put':
                        response = await session.put(url, json=payload, headers=self.headers)
                    else:
                        raise ValueError("Unsupported HTTP method")

                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        logger.error(f"HTTP Error {response.status}: {await response.text()}")
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed with error: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(10*attempt)
                else:
                    raise
        raise Exception("All retry attempts failed")

    async def create_empty_job(self, client: ClientSession, description: str, estimated_time: float, job_name: str, user_id: str) -> str:
        payload = {
            "id": str(uuid4()),
            "description": description,
            "estimated_time": estimated_time,
            "status": "unknown",
            "name": job_name,
            "user_id": user_id
        }
        url = f"{self.DATASERVICE_BASE_URL}/job/"
        resp_json = await self._request_with_retry('post', url, payload)
        logger.info(f"{resp_json=}")
        return str(resp_json["id"])

    async def update_job(self, client: ClientSession, job_id: str, payload: Optional[Any]) -> Optional[Any]:
        url = f"{self.DATASERVICE_BASE_URL}/job/{job_id}"
        resp_json = await self._request_with_retry('put', url, payload)
        logger.info(f"{resp_json=}")
        return resp_json
