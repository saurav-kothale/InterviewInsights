from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import os
import whisper
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from moviepy.editor import VideoFileClip
from dotenv import load_dotenv

interview_router = APIRouter()

# Setting up the path for ffmpeg
ffmpeg_path = r"ffmpeg-7.1-essentials_build\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Loading the Whisper model
whisper_model = whisper.load_model("base")

# Groq API key
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    raise Exception("GROQ_API_KEY not found in environment variables.")
llm = ChatGroq(model="llama3-70b-8192", groq_api_key=groq_api_key)

# Function to extract audio using moviepy
def extract_audio(video_path: str, audio_path: str):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    video.close()

@interview_router.post("/interview-analysis")
async def interview_analysis(interview: UploadFile = File(...)):
    try:
        # Save the uploaded video file
        temp_video_path = f"./{interview.filename}"
        temp_audio_path = "./audio.wav"
        
        with open(temp_video_path, "wb") as file:
            file.write(await interview.read())
        
        # Extract audio from video
        extract_audio(temp_video_path, temp_audio_path)

        # Convert audio to text (transcription)
        result = whisper_model.transcribe(temp_audio_path)
        transcription = result["text"]

        # Define the prompt for LLM
        prompt_template = f"""
        You are an expert in analyzing interviews. Given the following transcription of an interview, summarize the candidate's responses,
        and highlight key traits such as:
        1. Communication Style (How the candidate expresses ideas and conveys information)
        2. Active Listening (The candidate’s ability to understand and respond appropriately to questions)
        3. Engagement with the Interviewer (The level of interaction and rapport established during the interview)
        
        Interview Transcript:
        {transcription}
        Keep the response concise and cover all the points.
        """

        # Run the LLM chain
        prompt = PromptTemplate(input_variables=["transcription"], template=prompt_template)
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run({"transcription": transcription})

        # Clean up temporary files
        os.remove(temp_video_path)
        os.remove(temp_audio_path)

        # Return the response as JSON
        return JSONResponse(content={"interview_summary": response})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


