from fastapi import FastAPI, HTTPException
from typing import List, Optional
from config import collection
from bson.objectid import ObjectId
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
        
class Job(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    estimated_time: float
    user_id:str
    status:str = "unknown"
    created_at:datetime = datetime.now()
    updated_at:datetime = datetime.now()

class UpdateJob(BaseModel):
    name: Optional[str]
    description: Optional[str]
    estimated_time: Optional[float]
    status:Optional[str]
  


@app.post("/job/")
async def create_job(job: Job):
    job = jsonable_encoder(job)
    new_job = await collection.insert_one(job)
    return {"id":str(new_job.inserted_id)}

@app.get("/job/{user_id}", response_model=List[Job])
async def read_jobs(user_id:str):
    jobs = await collection.find({"user_id": user_id}).to_list(1000)
    return jobs

@app.get("/job/{job_id}", response_model=Job)
async def read_job(job_id: str):
    if (job := await collection.find_one({"_id": ObjectId(job_id)})) is not None:
        return job
    raise HTTPException(status_code=404, detail="Job not found")

@app.put("/job/{job_id}", response_model=UpdateJob)
async def update_job(job_id: str, job_update: UpdateJob):
    job = {k: v for k, v in job_update.dict().items() if v is not None}
    job = {
        **job,
        "updated_at":datetime.now()
    }
    if len(job) >= 1:
        update_result = await collection.update_one({"_id": ObjectId(job_id)}, {"$set": job})

        if update_result.modified_count == 1:
            if (updated_job := await collection.find_one({"_id": ObjectId(job_id)})) is not None:
                return updated_job

    if (existing_job := await collection.find_one({"_id": ObjectId(job_id)})) is not None:
        return existing_job

    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

@app.delete("/jobs/{job_id}", response_model=Job)
async def delete_job(job_id: str):
    delete_result = await collection.delete_one({"_id": ObjectId(job_id)})

    if delete_result.deleted_count == 1:
        return {"message": f"Job {job_id} deleted."}

    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
