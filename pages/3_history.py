import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import functions from main app
from app import check_scheduled_jobs

# Import st_aggrid
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

# Set page configuration
st.set_page_config(
    page_title="History - TaskFlow",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Main function for the history page
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

    st.title("Job Execution History")

    if st.button("Back", use_container_width=True):
        st.switch_page("app.py")
    
    # Check and execute scheduled jobs
    check_scheduled_jobs()
    
    if not st.session_state.job_history:
        st.info("No job execution history yet.")
    else:
        # Create a filter for job names
        job_names = ["All"] + sorted(list(set([job['name'] for job in st.session_state.jobs])))
        selected_job = st.selectbox("Filter by Job", options=job_names)
        
        # Sort history by timestamp (newest first)
        sorted_history = sorted(st.session_state.job_history, key=lambda x: x['timestamp'], reverse=True)
        
        # Filter by selected job if not "All"
        if selected_job != "All":
            filtered_history = []
            for history in sorted_history:
                for job in st.session_state.jobs:
                    if job['id'] == history['job_id'] and job['name'] == selected_job:
                        filtered_history.append(history)
                        break
            display_history = filtered_history
        else:
            display_history = sorted_history
        
        # Display history entries in a table format
        history_data = []
        for i, history in enumerate(display_history):
            job_name = next((job['name'] for job in st.session_state.jobs if job['id'] == history['job_id']), 'Unknown')
            timestamp = history['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            status = "✅ Success" if history['success'] else "❌ Failed"
            
            # Get arguments if they exist, otherwise show empty string
            arguments = history.get('arguments', '')
            
            history_data.append({
                "id": i,  # Add an ID for reference
                "Job Name": job_name,
                "Timestamp": timestamp,
                "Status": status,
                # Add arguments to history display (truncated if too long)
                "Arguments": arguments[:30] + ('...' if len(arguments) > 30 else '')
            })
        
        # Create DataFrame for display
        display_df = pd.DataFrame(history_data)
        
        # Configure AgGrid
        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_default_column(resizable=True, filterable=True)
        gb.configure_column("id", hide=True)  # Hide the ID column
        gb.configure_selection(selection_mode="single", use_checkbox=False)
        gb.configure_grid_options(domLayout='normal', rowHeight=35)
        grid_options = gb.build()
        
        # Display AgGrid
        grid_response = AgGrid(
            display_df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            theme="streamlit",
            height=min(350, len(display_df) * 35 + 50),  # Adjust height based on number of rows
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED
        )
        
        # Get selected rows - this is the part we need to fix
        selected_rows = grid_response["selected_rows"]
        
        # Check if there are any selected rows properly
        if isinstance(selected_rows, pd.DataFrame):
            has_selection = not selected_rows.empty
        else:
            if selected_rows:
                has_selection = len(selected_rows) > 0
            else:
                has_selection = 0
        
        # Display details for selected row
        if has_selection:
            if isinstance(selected_rows, pd.DataFrame):
                selected_index = selected_rows.iloc[0]["id"]
            else:
                selected_index = selected_rows[0]["id"]
                
            selected_history = display_history[selected_index]
            job_name = next((job['name'] for job in st.session_state.jobs if job['id'] == selected_history['job_id']), 'Unknown')
            
            # Display execution details
            st.subheader("Execution Details")
            
            # Create 4 columns for the metadata (adding the Arguments column)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**Job Name**")
                st.markdown(f"{job_name}")
            
            with col2:
                st.markdown("**Execution Time**")
                st.markdown(f"{selected_history['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col3:
                st.markdown("**Status**")
                status_color = "green" if selected_history['success'] else "red"
                status_text = "Success" if selected_history['success'] else "Failed"
                st.markdown(f"<span style='color:{status_color};'>{status_text}</span>", unsafe_allow_html=True)
            
            # Add a column for arguments
            with col4:
                st.markdown("**Arguments**")
                arguments = selected_history.get('arguments', '')
                st.markdown(f"`{arguments}`" if arguments else "No arguments")
            
            # Create tabs for output and error
            tab1, tab2 = st.tabs(["Output", "Error"])
            
            with tab1:
                if selected_history['output']:
                    st.code(selected_history['output'])
                else:
                    st.info("No output recorded")
            
            with tab2:
                if selected_history['error']:
                    st.code(selected_history['error'])
                else:
                    st.info("No errors recorded")

# Run the page
if __name__ == "__main__":
    main()