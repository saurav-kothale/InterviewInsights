import os
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import shutil
from model.model import llm, embeddings
from fastapi.responses import StreamingResponse
from io import StringIO

job_router = APIRouter()

load_dotenv()

class JobDescription(BaseModel):
    title: str
    description: str

class JobDescriptionsRequest(BaseModel):
    job_descriptions: List[JobDescription]


# Define prompt for matching resume with job descriptions
prompt_template = """
Based on this resume:
{resume}
Compare it with the job description:
{job_description}
You are an expert in matching resumes with job descriptions. You can provide response by SORTING each job RANK-WISE.
Provide the following information about each job role concisely:
1. Job role/title.
2. Analytics to show why the candidate is a good fit, highlighting:
    - Rank among all job descriptions (e.g., if there are 3 jobs, rank them from 1 to 3).
    - Skill match percentage.
    - How the candidate's experience aligns with job requirements.
    - Relevance of degree and certifications.
    - Tools and technologies mentioned in both the resume and job description.
    - Matching score out of 10.
"""

prompt = PromptTemplate(input_variables=["resume", "job_description"], template=prompt_template)
chain = LLMChain(llm=llm, prompt=prompt)

@job_router.post("/upload-resume")
async def upload_resume(
    resume: UploadFile = File(...),
    title: list[str] = Body(...),
    description: list[str] = Body(...),
    # resume: UploadFile = File(...),
    
):
    try:
        file_name = resume.filename
        file_path = f"./{file_name}"
        
        # Save the uploaded resume file temporarily
        with open(file_path, "wb") as file:
            shutil.copyfileobj(resume.file, file)
        
        # Load the resume content based on file type
        if file_name.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_name.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format.")
        
        # Process and extract text from the resume
        docs = loader.load()
        resume_text = docs[0].page_content
        
        # Clean up the saved file after processing
        os.remove(file_path)
        
        # Retrieve job descriptions from the request
        # job_descriptions = description
        
        # Concatenate job descriptions for similarity matching
        job_description_text = ' '.join(
            [f"Job Title: {title}\nDescription: {job}" for job in description]
        )
        
        # Run the prompt chain for recommendations
        result = chain.run({"resume": resume_text, "job_description": job_description_text})

        stream = StringIO(result)
        
        # Return the result as JSON response
        return StreamingResponse(stream, media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")