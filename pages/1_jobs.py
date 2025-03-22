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
    page_title="All Jobs - ScriptFlow",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Function to toggle job status
def toggle_job_status(job_id):
    for i, job in enumerate(st.session_state.jobs):
        if job['id'] == job_id:
            # Toggle the enabled status
            new_status = not job['enabled']
            st.session_state.jobs[i]['enabled'] = new_status
            
            # Update next run time if the job is now enabled
            if new_status:
                last_run = job['last_run'] or datetime.datetime.now()
                st.session_state.next_run_times[job_id] = last_run + datetime.timedelta(seconds=job['interval_seconds'])
            
            # Save data
            save_data()
            
            return True
    
    return False

# Function to delete a job
def delete_job(job_id):
    for i, job in enumerate(st.session_state.jobs):
        if job['id'] == job_id:
            # Remove the script file
            try:
                os.remove(job['script_path'])
            except:
                pass
            
            # Remove the job from session state
            st.session_state.jobs.pop(i)
            
            # Remove the job from next run times
            if job_id in st.session_state.next_run_times:
                del st.session_state.next_run_times[job_id]
            
            # Save data
            save_data()
            
            return True
    
    return False

# Main function for the jobs page
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

    st.title("All Jobs")
    
    # Check and execute scheduled jobs
    check_scheduled_jobs()
    
    if not st.session_state.jobs:
        st.info("No jobs scheduled. Go to the 'Add Job' page to create one.")
        if st.button("Create Job"):
            st.switch_page("pages/2_add_job.py")
    else:
        # Set up edit form first so we can check if we're in edit mode
        edit_container = st.container()
        
        with edit_container:
            # Show edit form if requested
            if 'show_edit_form' in st.session_state and st.session_state.show_edit_form:
                st.subheader("Edit Job")
                
                # Find the job to edit
                edit_job = None
                for job in st.session_state.jobs:
                    if job['id'] == st.session_state.edit_job_id:
                        edit_job = job
                        break
                
                if edit_job:
                    with st.form(key="edit_job_form"):
                        name = st.text_input("Job Name", value=edit_job['name'])
                        
                        script_type = st.selectbox(
                            "Script Type",
                            options=["py", "sh", "php", "js", "rb", "pl", "ps1", "bat", "cmd", "r", "lua", "go", "sql"],
                            index=["py", "sh", "php", "js", "rb", "pl", "ps1", "bat", "cmd", "r", "lua", "go", "sql"].index(edit_job['script_type']) if edit_job['script_type'] in ["py", "sh", "php", "js", "rb", "pl", "ps1", "bat", "cmd", "r", "lua", "go", "sql"] else 0
                        )
                        
                        script_content = st.text_area(
                            "Script Content",
                            value=st.session_state.edit_job_content,
                            height=300
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            interval_value = st.number_input("Interval Value", min_value=1, value=edit_job['interval_value'])
                        
                        with col2:
                            interval_unit = st.selectbox(
                                "Interval Unit",
                                options=["minutes", "hours", "days"],
                                index=["minutes", "hours", "days"].index(edit_job['interval_unit']) if edit_job['interval_unit'] in ["minutes", "hours", "days"] else 0
                            )
                        
                        enabled = st.checkbox("Enabled", value=edit_job['enabled'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            submit = st.form_submit_button("Update Job", use_container_width=True)
                        
                        with col2:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state.show_edit_form = False
                                st.rerun()
                        
                        if submit:
                            # Import update_job function
                            from app import update_job
                            
                            if update_job(
                                st.session_state.edit_job_id,
                                name,
                                script_content,
                                script_type,
                                interval_value,
                                interval_unit,
                                enabled
                            ):
                                # Set a flag to show success message outside the form
                                st.session_state.job_updated = name
                                st.session_state.show_edit_form = False
                                st.rerun()
                            else:
                                st.error("Failed to update job.")
        
        # Only show the job list if not in edit mode
        if 'show_edit_form' not in st.session_state or not st.session_state.show_edit_form:
            jobs_container = st.container()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Back", use_container_width=True):
                    st.switch_page("app.py")
            with col2:
                # Add button to create new job
                if st.button("➕ Create new Job", use_container_width=True):
                    st.switch_page("pages/2_add_job.py")
            
            with jobs_container:
                # Create a container for each job
                for job in st.session_state.jobs:
                    # Check if this is the newly added job to auto-expand it
                    default_expanded = 'newly_added_job' in st.session_state and job['id'] == st.session_state.newly_added_job
                    
                    # Create a container for each job with status emoji in the title
                    with st.expander(f"{status_indicator(job['enabled'], use_emoji=True)}{job['name']} ({job['script_type']})", expanded=default_expanded):
                        # If this was a newly added job, clear the flag after expanding it
                        if default_expanded:
                            # Clear the flag after this render cycle
                            del st.session_state.newly_added_job
                        
                        # Additional status indicator inside with more details
                        # status_text = "Enabled" if job['enabled'] else "Disabled"
                        # st.markdown(f"{status_indicator(job['enabled'])} **Status: {status_text}**", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Interval:** Every {job['interval_value']} {job['interval_unit']}")
                            
                            if job['last_run']:
                                st.write(f"**Last Run:** {job['last_run'].strftime('%Y-%m-%d %H:%M:%S')}")
                            else:
                                st.write("**Last Run:** Never")
                            
                            if job['enabled'] and job['id'] in st.session_state.next_run_times:
                                st.write(f"**Next Run:** {st.session_state.next_run_times[job['id']].strftime('%Y-%m-%d %H:%M:%S')}")
                            else:
                                st.write("**Next Run:** Disabled")
                        
                        with col2:
                            # Use 4-column layout for buttons
                            button_cols = st.columns(4)
                            
                            with button_cols[0]:
                                if st.button("Run", key=f"run_{job['id']}", use_container_width=True):
                                    success, output = execute_script(job['id'], job['script_path'], job['script_type'])
                                    if success:
                                        st.success("Job executed successfully!")
                                    else:
                                        st.error(f"Job execution failed: {output}")
                                    
                                    # Update last run time
                                    for i, j in enumerate(st.session_state.jobs):
                                        if j['id'] == job['id']:
                                            st.session_state.jobs[i]['last_run'] = datetime.datetime.now()
                                            break
                                    
                                    # Save data
                                    save_data()
                            
                            with button_cols[1]:
                                status_btn_text = "Disable" if job['enabled'] else "Enable"
                                if st.button(status_btn_text, key=f"toggle_{job['id']}", use_container_width=True):
                                    if toggle_job_status(job['id']):
                                        st.success(f"Job {status_btn_text.lower()}d successfully!")
                                        st.rerun()
                            
                            with button_cols[2]:
                                if st.button("History", key=f"history_{job['id']}", use_container_width=True):
                                    st.switch_page("pages/3_history.py")
                                    st.rerun()
                            
                            with button_cols[3]:
                                if st.button("Edit", key=f"edit_{job['id']}", use_container_width=True):
                                    st.session_state.edit_job_id = job['id']
                                    st.session_state.edit_job_content = get_script_content(job['script_path'])
                                    st.session_state.show_edit_form = True
                                    st.rerun()
                            
                            # Use the same column for delete button
                            with button_cols[3]:
                                if st.button("Delete", key=f"delete_{job['id']}", use_container_width=True):
                                    if delete_job(job['id']):
                                        st.success("Job deleted successfully!")
                                        st.rerun()
                        
                        # Show script content
                        st.markdown("---")
                        st.subheader("Script Content")
                        script_content = get_script_content(job['script_path'])
                        st.code(script_content, language=job['script_type'])
            
            # Show success message outside the form
            if 'job_updated' in st.session_state:
                st.success(f"Job '{st.session_state.job_updated}' updated successfully!")
                # Clear the flag after displaying the message
                del st.session_state.job_updated

# Run the page
if __name__ == "__main__":
    main()