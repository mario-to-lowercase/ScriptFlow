import streamlit as st
import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from main app
from app import status_indicator, save_data, get_script_content, execute_script, check_scheduled_jobs

# Set page configuration
st.set_page_config(
    page_title="Run Job - TaskFlow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

    st.title("Run Job")
    
    # Check and execute scheduled jobs
    check_scheduled_jobs()
    
    # Navigation button
    if st.button("Back to Jobs", use_container_width=True):
        st.switch_page("pages/1_jobs.py")
    
    # Check if we have a job ID to run
    if 'run_job_id' not in st.session_state:
        st.warning("No job selected to run. Please select a job from the Jobs page.")
        return
    
    # Get the job info
    job_id = st.session_state.run_job_id
    selected_job = None
    
    for job in st.session_state.jobs:
        if job['id'] == job_id:
            selected_job = job
            break
    
    if not selected_job:
        st.error("The selected job was not found. It may have been deleted.")
        if st.button("Return to Jobs List"):
            st.switch_page("pages/1_jobs.py")
        return
    
    # Get all job names for the dropdown
    job_options = {}
    for job in st.session_state.jobs:
        job_options[job['name']] = job['id']
    
    # Show job selection dropdown
    selected_job_name = st.selectbox(
        "Select Job to Run",
        options=list(job_options.keys()),
        index=list(job_options.keys()).index(selected_job['name']) if selected_job['name'] in job_options else 0
    )
    
    # Update selected job if changed
    if job_options[selected_job_name] != job_id:
        st.session_state.run_job_id = job_options[selected_job_name]
        st.rerun()
    
    # Main run form area - using Streamlit's built-in components
    st.subheader("Run Job Settings")
    
    # Use a Streamlit native expander for the job details
    with st.expander("Job Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Name:** {selected_job['name']}")
            st.write(f"**Type:** {selected_job['script_type']}")
        
        with col2:
            st.write(f"**Last Run:** {selected_job['last_run'].strftime('%Y-%m-%d %H:%M:%S') if selected_job['last_run'] else 'Never'}")
            if 'script_arguments' in selected_job and selected_job['script_arguments']:
                st.write(f"**Default Arguments:** `{selected_job['script_arguments']}`")
    
    # Arguments field with default arguments
    st.write("**Execution Settings**")
    default_args = selected_job.get('script_arguments', '')
    run_args = st.text_input(
        "Arguments", 
        value=default_args,
        help="Space-separated arguments to pass to the script"
    )
    
    # Run button
    if st.button("Run Job Now", use_container_width=True, type="primary"):
        # Execute the script with provided arguments
        success, output = execute_script(
            selected_job['id'], 
            selected_job['script_path'], 
            selected_job['script_type'],
            run_args
        )
        
        # Store result in session state
        st.session_state.run_success = success
        st.session_state.run_output = output
        
        # Update last run time
        for i, j in enumerate(st.session_state.jobs):
            if j['id'] == selected_job['id']:
                st.session_state.jobs[i]['last_run'] = datetime.datetime.now()
                break
        
        # Save data
        save_data()
        
        # Rerun to show results
        st.rerun()
    
    # Script preview
    with st.expander("Script Content", expanded=False):
        script_content = get_script_content(selected_job['script_path'])
        st.code(script_content, language=selected_job['script_type'])
    
    # Show execution results if available
    if 'run_success' in st.session_state:
        st.divider()  # Add a visual separator
        st.subheader("Execution Results")
        
        if st.session_state.run_success:
            st.success("Job executed successfully!")
            
            # Show output if there is any
            if st.session_state.run_output:
                with st.expander("Output", expanded=True):
                    st.code(st.session_state.run_output)
            else:
                st.info("The job completed with no output.")
        else:
            st.error("Job execution failed!")
            with st.expander("Error Details", expanded=True):
                st.code(st.session_state.run_output)
        
        # Add a button to clear results
        if st.button("Clear Results"):
            del st.session_state.run_success
            del st.session_state.run_output
            st.rerun()

# Run the page
if __name__ == "__main__":
    main()