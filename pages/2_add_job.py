import streamlit as st

# Set page configuration - this must be the first Streamlit command
st.set_page_config(
    page_title="Create Job - ScriptFlow",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Only import other modules after st.set_page_config()
import sys
import os
import datetime
import uuid
import json
from pathlib import Path

# Create a direct reference to needed functions without importing the app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import specific functions from app instead of the whole module
from app import add_job, check_scheduled_jobs, create_script_file

# Main function for the add job page
def main():
    # Hide the deploy button/text with custom CSS
    hide_deploy_text = """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_deploy_text, unsafe_allow_html=True)

    st.title("Create Job")

    if st.button("Back", use_container_width=True):
        st.switch_page("app.py")
    
    # Check and execute scheduled jobs
    check_scheduled_jobs()
    
    # Initialize session state for tracking job creation
    if 'job_just_created' not in st.session_state:
        st.session_state.job_just_created = False
        st.session_state.created_job_name = ""

    # Check if we should show the form or success message
    if not st.session_state.job_just_created:
        # Show the form for creating a new job
        with st.form(key="add_job_form"):
            name = st.text_input("Job Name")
            
            script_type = st.selectbox(
                "Script Type",
                options=["py", "sh", "php", "js", "rb", "pl", "ps1", "bat", "cmd", "r", "lua", "go", "sql"]
            )
            
            script_content = st.text_area("Script Content", height=300, placeholder="Enter your code here...") 
            
            col1, col2 = st.columns(2)
            with col1:
                interval_value = st.number_input("Interval", min_value=1, value=1)
            
            with col2:
                interval_unit = st.selectbox(
                    "Unit",
                    options=["minutes", "hours", "days"]
                )
            
            # Add the enabled/disabled toggle
            enabled = st.toggle("Enabled", value=True, help="Enable or disable the job")
            
            # Submit button
            submit = st.form_submit_button("Create Job", use_container_width=True)
            
            if submit:
                if name and script_content:
                    # Add the job and get its ID
                    job_id = add_job(name, script_content, script_type, interval_value, interval_unit, enabled)
                    
                    # Store the ID of the newly created job to auto-expand it on the jobs page
                    st.session_state.newly_added_job = job_id
                    
                    # Set session state to indicate job was created
                    st.session_state.job_just_created = True
                    st.session_state.created_job_name = name
                    
                    # Rerun the app to show the success message instead of the form
                    st.rerun()
                else:
                    st.error("Provide a name and script content to create a job.")
    else:
        # Show success message and button when job was created
        st.success(f"Job '{st.session_state.created_job_name}' created successfully!")
        
        # Add a button to create another job
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create another Job", use_container_width=True):
                # Reset the session state and rerun to show the form again
                st.session_state.job_just_created = False
                st.session_state.created_job_name = ""
                st.rerun()
        
        with col2:
            if st.button("Show Job", use_container_width=True):
                st.switch_page("pages/1_jobs.py")

# Run the page
if __name__ == "__main__":
    main()