import pandas as pd
import datetime
import time
import os
import uuid
import subprocess
import json
from pathlib import Path
import streamlit as st

# File paths for persistent storage
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
JOBS_FILE = DATA_DIR / "jobs.json"
HISTORY_FILE = DATA_DIR / "history.json"


# Function to create a status indicator
def status_indicator(enabled, use_emoji=False):
    if use_emoji:
        # Use Unicode emoji for status indicators in expander headers
        return "🟢 " if enabled else "🔴 "
    else:
        # Use HTML for status indicators inside expandable content
        status_class = "enabled" if enabled else "disabled"
        dot_html = f'<span class="status-dot {status_class}"></span>'
        return dot_html

# Load jobs and history from files
def load_data():
    if 'jobs' not in st.session_state:
        if JOBS_FILE.exists():
            try:
                with open(JOBS_FILE, 'r') as f:
                    jobs_data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for job in jobs_data:
                        job['created_at'] = datetime.datetime.fromisoformat(job['created_at'])
                        if job['last_run']:
                            job['last_run'] = datetime.datetime.fromisoformat(job['last_run'])
                    st.session_state.jobs = jobs_data
            except Exception as e:
                st.error(f"Error loading jobs: {str(e)}")
                st.session_state.jobs = []
        else:
            st.session_state.jobs = []
    
    if 'job_history' not in st.session_state:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r') as f:
                    history_data = json.load(f)
                    # Convert string timestamps back to datetime objects
                    for entry in history_data:
                        entry['timestamp'] = datetime.datetime.fromisoformat(entry['timestamp'])
                    st.session_state.job_history = history_data
            except Exception as e:
                st.error(f"Error loading history: {str(e)}")
                st.session_state.job_history = []
        else:
            st.session_state.job_history = []
    
    if 'next_run_times' not in st.session_state:
        st.session_state.next_run_times = {}
        # Recalculate next run times based on loaded jobs
        for job in st.session_state.jobs:
            if job['enabled']:
                last_run = job['last_run'] or datetime.datetime.now()
                st.session_state.next_run_times[job['id']] = last_run + datetime.timedelta(seconds=job['interval_seconds'])

# Save jobs and history to files
def save_data():
    try:
        # Convert datetime objects to strings for JSON serialization
        jobs_data = []
        for job in st.session_state.jobs:
            job_copy = job.copy()
            job_copy['created_at'] = job_copy['created_at'].isoformat()
            if job_copy['last_run']:
                job_copy['last_run'] = job_copy['last_run'].isoformat()
            jobs_data.append(job_copy)
        
        with open(JOBS_FILE, 'w') as f:
            json.dump(jobs_data, f, indent=2)
        
        history_data = []
        for entry in st.session_state.job_history:
            entry_copy = entry.copy()
            entry_copy['timestamp'] = entry_copy['timestamp'].isoformat()
            history_data.append(entry_copy)
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

# Function to check and execute scheduled jobs
def check_scheduled_jobs():
    # Load data if not already loaded
    load_data()
    
    now = datetime.datetime.now()
    jobs_executed = False
    
    for job in st.session_state.jobs:
        job_id = job['id']
        
        # Skip disabled jobs
        if not job['enabled']:
            continue
        
        # Check if it's time to run the job
        if job_id in st.session_state.next_run_times and now >= st.session_state.next_run_times[job_id]:
            # Execute the job
            success, output = execute_script(job_id, job['script_path'], job['script_type'])
            jobs_executed = True
            
            # Update last run time
            for i, j in enumerate(st.session_state.jobs):
                if j['id'] == job_id:
                    st.session_state.jobs[i]['last_run'] = now
                    break
            
            # Schedule next run
            st.session_state.next_run_times[job_id] = now + datetime.timedelta(seconds=job['interval_seconds'])
    
    # Save data if any jobs were executed
    if jobs_executed:
        save_data()

# Function to execute a script
def execute_script(job_id, script_path, script_type):
    try:
        if script_type == 'py':
            result = subprocess.run(['python', script_path], capture_output=True, text=True)
        elif script_type == 'sh':
            result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        elif script_type == 'php':
            result = subprocess.run(['php', script_path], capture_output=True, text=True)
        elif script_type == 'js':
            result = subprocess.run(['node', script_path], capture_output=True, text=True)
        elif script_type == 'rb':
            result = subprocess.run(['ruby', script_path], capture_output=True, text=True)
        elif script_type == 'pl':
            result = subprocess.run(['perl', script_path], capture_output=True, text=True)
        elif script_type == 'ps1':
            result = subprocess.run(['powershell', '-File', script_path], capture_output=True, text=True)
        elif script_type == 'bat' or script_type == 'cmd':
            result = subprocess.run([script_path], shell=True, capture_output=True, text=True)
        elif script_type == 'r':
            result = subprocess.run(['Rscript', script_path], capture_output=True, text=True)
        elif script_type == 'lua':
            result = subprocess.run(['lua', script_path], capture_output=True, text=True)
        elif script_type == 'go':
            result = subprocess.run(['go', 'run', script_path], capture_output=True, text=True)
        elif script_type == 'sql':
            # Generic SQL execution - would need to be customized for specific DB engines
            result = subprocess.run(['sqlite3', '-init', script_path, ':memory:', '.exit'], capture_output=True, text=True)
        else:
            return False, f"Unsupported script type: {script_type}"
        
        # Record the execution in history
        st.session_state.job_history.append({
            'job_id': job_id,
            'timestamp': datetime.datetime.now(),
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        })
        
        # Save history data
        save_data()
        
        return result.returncode == 0, result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        error_message = str(e)
        
        # Record the execution failure in history
        st.session_state.job_history.append({
            'job_id': job_id,
            'timestamp': datetime.datetime.now(),
            'success': False,
            'output': '',
            'error': error_message
        })
        
        # Save history data
        save_data()
        
        return False, error_message

# Function to create a temporary script file
def create_script_file(content, script_type):
    # Create a scripts directory if it doesn't exist
    script_dir = Path("scripts")
    script_dir.mkdir(exist_ok=True)
    
    # Generate a unique filename
    script_id = str(uuid.uuid4())
    filename = script_dir / f"{script_id}.{script_type}"
    
    # Write content to the file
    with open(filename, 'w') as f:
        f.write(content)
    
    # Make the file executable for script types that require it
    if script_type in ['sh', 'pl', 'rb', 'py', 'php', 'js', 'lua', 'r', 'bat', 'cmd']:
        os.chmod(filename, 0o755)
    
    return filename

# Function to get script content
def get_script_content(script_path):
    try:
        with open(script_path, 'r') as f:
            return f.read()
    except:
        return "Error reading script content."

# Function to add a new job
def add_job(name, script_content, script_type, interval_value, interval_unit, enabled=True):
    # Convert interval to seconds
    interval_seconds = interval_value
    if interval_unit == "minutes":
        interval_seconds *= 60
    elif interval_unit == "hours":
        interval_seconds *= 3600
    elif interval_unit == "days":
        interval_seconds *= 86400
    
    # Create the script file
    script_path = create_script_file(script_content, script_type)
    
    # Generate a unique ID for the job
    job_id = str(uuid.uuid4())
    
    # Create the job object with ALL fields for consistency
    job = {
        'id': job_id,
        'name': name,
        'script_path': str(script_path),
        'script_type': script_type,
        'interval_value': interval_value,  # Add this field
        'interval_unit': interval_unit,    # Add this field
        'interval_seconds': interval_seconds,
        'created_at': datetime.datetime.now(),
        'last_run': None,
        'enabled': enabled
    }
    
    # Add the job to the session state
    st.session_state.jobs.append(job)
    
    # Schedule the next run if the job is enabled
    if enabled:
        st.session_state.next_run_times[job_id] = datetime.datetime.now() + datetime.timedelta(seconds=interval_seconds)
    
    # Save the updated jobs data
    save_data()
    
    return job_id

# Function to update an existing job
def update_job(job_id, name, script_content, script_type, interval_value, interval_unit, enabled):
    try:
        # Find the job to update
        job_index = None
        for i, job in enumerate(st.session_state.jobs):
            if job['id'] == job_id:
                job_index = i
                break
        
        if job_index is None:
            return False
        
        # Convert interval to seconds
        interval_seconds = interval_value
        if interval_unit == "minutes":
            interval_seconds *= 60
        elif interval_unit == "hours":
            interval_seconds *= 3600
        elif interval_unit == "days":
            interval_seconds *= 86400
        
        # Create a new script file if the content has changed
        old_script_path = st.session_state.jobs[job_index]['script_path']
        old_script_content = get_script_content(old_script_path)
        
        if script_content != old_script_content or script_type != st.session_state.jobs[job_index]['script_type']:
            # Create a new script file
            script_path = create_script_file(script_content, script_type)
            
            # Remove the old script file
            try:
                os.remove(old_script_path)
            except:
                pass
        else:
            # Keep the existing script file
            script_path = old_script_path
        
        # Update the job
        st.session_state.jobs[job_index]['name'] = name
        st.session_state.jobs[job_index]['script_path'] = str(script_path)
        st.session_state.jobs[job_index]['script_type'] = script_type
        st.session_state.jobs[job_index]['interval_value'] = interval_value  # Add this field
        st.session_state.jobs[job_index]['interval_unit'] = interval_unit    # Add this field
        st.session_state.jobs[job_index]['interval_seconds'] = interval_seconds
        st.session_state.jobs[job_index]['enabled'] = enabled
        
        # Update next run time if enabled
        if enabled:
            last_run = st.session_state.jobs[job_index]['last_run'] or datetime.datetime.now()
            st.session_state.next_run_times[job_id] = last_run + datetime.timedelta(seconds=interval_seconds)
        elif job_id in st.session_state.next_run_times:
            del st.session_state.next_run_times[job_id]
        
        # Save data
        save_data()
        
        return True
    except Exception as e:
        print(f"Error updating job: {str(e)}")
        return False

def custom_metric(label, value, color):
    html = f"""
    <div style="text-align: center;">
        <p style="font-size:1.8em; margin-bottom: 0.2em;">{label}</p>
        <p style="font-size:1.8em; font-weight: bold; color: {color}; margin: 0;">{value}</p>
    </div>
    """
    return html

# Main page - Only execute when run directly (not when imported)
def main():
    # Set page configuration - this is now inside the main function
    st.set_page_config(
        page_title="ScriptFlow",
        page_icon="⏱️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Add custom CSS for status dots
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .status-dot {
            display: inline-block;
            height: 10px;
            width: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .enabled {
            background-color: #32CD32; /* Green */
        }
        .disabled {
            background-color: #FF4500; /* Red */
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Check and execute scheduled jobs
    check_scheduled_jobs()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(custom_metric("Total Jobs", len(st.session_state.jobs), "white"), unsafe_allow_html=True)
    
    with col2:
        active_jobs = sum(1 for job in st.session_state.jobs if job['enabled'])
        st.markdown(custom_metric("Active Jobs", active_jobs, "green"), unsafe_allow_html=True)
        
    with col3:
        inactive_jobs = sum(1 for job in st.session_state.jobs if job['enabled'] == False)
        st.markdown(custom_metric("Inactive Jobs", inactive_jobs, "red"), unsafe_allow_html=True)
    
    st.divider()

    # Quick links
    st.header("Quick Links")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("All Jobs", use_container_width=True):
            st.switch_page("pages/1_jobs.py")
    
    with col2:
        if st.button("Create Job", use_container_width=True):
            st.switch_page("pages/2_add_job.py")
    
    with col3:
        if st.button("Job History", use_container_width=True):
            st.switch_page("pages/3_history.py")
    
    with col4:
        if st.button("Templates", use_container_width=True):
            st.switch_page("pages/4_templates.py")
    
    st.divider()

    # Show recently executed jobs
    st.header("Recently Executed Jobs")
    
    if not st.session_state.job_history:
        st.info("No recemtly executed jobs yet.")
    else:
        # Get the 5 most recent job executions
        recent_history = sorted(st.session_state.job_history, key=lambda x: x['timestamp'], reverse=True)[:5]
        
        # Create a DataFrame for display
        history_data = []
        for history in recent_history:
            job_name = next((job['name'] for job in st.session_state.jobs if job['id'] == history['job_id']), 'Unknown')
            status = "Success" if history['success'] else "Failed"
            timestamp = history['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            
            history_data.append({
                "Job": job_name,
                "Timestamp": timestamp,
                "Status": status
            })
        
        history_df = pd.DataFrame(history_data)
        st.dataframe(history_df, use_container_width=True)

# Only run the main function when this script is executed directly
if __name__ == "__main__":
    main()