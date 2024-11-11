# import os
# import streamlit as st
# import Recruiter.jobs as jobs
# import User.user as user
# import interview_analysis.route as analysis


# ## Streamlit app

# def main():
#     st.sidebar.title("Choose your Functionality")
#     options=["Home","Recruiter","User","Interview Analysis"]
#     choice=st.sidebar.selectbox("Functionalities",options,index=0)
    
#     if choice=="Home":
#         st.title("👨🏻‍💼 : Job Matching and Candidate Analysis System")
#         st.subheader("A tool that enhances the recruitment process by automating the alignment of resumes with job requirements and evaluating interview content.")
#         st.write("Go ahead and give it a try!!!")
        
#     elif choice=="Recruiter":
#         st.header("Recruiter Dashboard")
#         jobs.run()
    
#     elif choice=="User":
#         st.header("User Dashboard")
#         user.run()
        
#     elif choice=="Interview Analysis":
#         st.header("Interview Analysis")
#         analysis.run()
        
# if __name__=="__main__":
#     main()

from fastapi import FastAPI
from source.interview_analysis.route import interview_router
from source.job_match_analysis.route import job_router
import uvicorn

app = FastAPI()


app.include_router(interview_router)
app.include_router(job_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload= True)