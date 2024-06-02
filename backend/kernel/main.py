from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Header, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware

from aiohttp import ClientSession
from loguru import logger
import asyncio
import datetime


from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from config.env import settings
from message_utils import send_message
import os
from ds_client import DataServiceClient
from http_client import HttpClient

#kernel

http_client = HttpClient()

app = FastAPI()


@app.on_event("startup")
async def startup():
    http_client.start()


@app.on_event("shutdown")
async def shutdown():
    await http_client.stop()

class JobExecutionRequest(BaseModel):
    job_name:str
    user_id: str
    description: Optional[str]
    estimated_time: float
    
class JobExecutorEnum(str, Enum):
    STANDARD = "standard"
    FAST = "fast"


async def fast_executor(client: ClientSession,job_id:str,request:JobExecutionRequest)->None:
  ds_client = DataServiceClient(DATASERVICE_BASE_URL=settings.DATA_SERVICE_URL)
  try:
    await ds_client.update_job(client=client,job_id=job_id,payload={"status":"running"})
    await asyncio.sleep(request.estimated_time)
    await ds_client.update_job(client=client,job_id=job_id,payload={"status":"completed"})
  except Exception as e:
    await ds_client.update_job(client=client,job_id=job_id,payload={"status":"failed"})
  

@app.post("/api/v1/job_executor/async")
async def job_executor_async(
    request: JobExecutionRequest,
    background_tasks: BackgroundTasks,
    client: ClientSession = Depends(http_client),
    executor: JobExecutorEnum = Query(JobExecutorEnum.FAST),
):
    start = datetime.datetime.now()

    logger.info(request)
    job_id = await get_async_context(client, request)
    if executor == JobExecutorEnum.FAST:
      background_tasks.add_task(fast_executor,client,job_id,request)
      # await fast_executor(client,job_id,request)
    else:
      await send_message(queue_name=os.environ['STANDARD_QUEUE_NAME'],payload=request.dict(),job_id=job_id)
    response = {"status": 200, "job_id": job_id}
    logger.info(f"Response object saved in request response logs: {response}")

    end = datetime.datetime.now()
    
    return response


async def get_async_context(
    client: ClientSession,
    request: JobExecutionRequest,
) -> Dict:
    ds_client = DataServiceClient(DATASERVICE_BASE_URL=settings.DATA_SERVICE_URL)
    return await ds_client.create_empty_job(client=client,description=request.description,estimated_time=request.estimated_time,user_id=request.user_id,job_name=request.job_name)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
