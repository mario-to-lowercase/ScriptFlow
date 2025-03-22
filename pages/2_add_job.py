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

# Function to load templates
def load_templates():
    """Load all job templates from the templates directory"""
    templates_dir = Path("templates")
    templates = {"None": None}  # Default option
    
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                    # Use the filename without extension as template name if not specified in the JSON
                    template_name = template_data.get("name", template_file.stem)
                    templates[template_name] = template_data
            except Exception as e:
                st.error(f"Error loading template {template_file}: {e}")
                
    return templates

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
    
    # Initialize all form field session states if they don't exist
    if 'job_name' not in st.session_state:
        st.session_state.job_name = ""
    if 'script_type' not in st.session_state:
        st.session_state.script_type = "py"
    if 'script_content' not in st.session_state:
        st.session_state.script_content = ""
    if 'interval_value' not in st.session_state:
        st.session_state.interval_value = 1
    if 'interval_unit' not in st.session_state:
        st.session_state.interval_unit = "minutes"
    if 'job_enabled' not in st.session_state:
        st.session_state.job_enabled = True

    # Check if we should show the form or success message
    if not st.session_state.job_just_created:
        # Load templates
        templates = load_templates()
        
        # Function to update form values when template changes
        def on_template_change():
            template_name = st.session_state.template_selection
            if template_name != "None" and templates[template_name] is not None:
                template = templates[template_name]
                # Directly update session state for each form field
                st.session_state.job_name = template.get("name", "")
                st.session_state.script_type = template.get("script-type", "py")
                st.session_state.script_content = template.get("script-content", "")
                st.session_state.interval_value = template.get("interval", 1)
                st.session_state.interval_unit = template.get("interval-unit", "minutes")
                st.session_state.job_enabled = template.get("enabled", True)
        
        # Template selector outside the form
        st.selectbox(
            "Select a Template",
            options=list(templates.keys()),
            index=0,  # Default to "None"
            key="template_selection",
            on_change=on_template_change
        )
        
        # Show the form for creating a new job
        with st.form(key="add_job_form"):
            name = st.text_input("Job Name", value=st.session_state.job_name, key="job_name")
            
            script_type_options = ["py", "sh", "php", "js", "rb", "pl", "ps1", "bat", "cmd", "r", "lua", "go", "sql"]
            script_type = st.selectbox(
                "Script Type",
                options=script_type_options,
                index=script_type_options.index(st.session_state.script_type) if st.session_state.script_type in script_type_options else 0,
                key="script_type"
            )
            
            script_content = st.text_area(
                "Script Content", 
                value=st.session_state.script_content,
                height=300, 
                placeholder="Enter your code here...",
                key="script_content"
            ) 
            
            col1, col2 = st.columns(2)
            with col1:
                interval_value = st.number_input(
                    "Interval", 
                    min_value=1, 
                    value=st.session_state.interval_value,
                    key="interval_value"
                )
            
            with col2:
                interval_units = ["minutes", "hours", "days"]
                interval_unit = st.selectbox(
                    "Unit",
                    options=interval_units,
                    index=interval_units.index(st.session_state.interval_unit) if st.session_state.interval_unit in interval_units else 0,
                    key="interval_unit"
                )
            
            # Add the enabled/disabled toggle
            enabled = st.toggle(
                "Enabled", 
                value=st.session_state.job_enabled, 
                help="Enable or disable the job",
                key="job_enabled"
            )
            
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
                    
                    # Reset form fields
                    st.session_state.job_name = ""
                    st.session_state.script_type = "py"
                    st.session_state.script_content = ""
                    st.session_state.interval_value = 1
                    st.session_state.interval_unit = "minutes"
                    st.session_state.job_enabled = True
                    
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