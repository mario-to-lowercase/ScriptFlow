import streamlit as st
import os
import json
from pathlib import Path
import re

# Set page configuration - this must be the first Streamlit command
st.set_page_config(
    page_title="Templates - ScriptFlow",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Function to convert a template name to a safe filename
def safe_filename(name):
    """Convert a template name to a safe filename"""
    # Replace spaces with hyphens and remove any special characters
    return re.sub(r'[^a-zA-Z0-9_-]', '', name.replace(' ', '-').lower())

# Function to load templates
def load_templates():
    """Load all job templates from the templates directory"""
    templates_dir = Path("templates")
    templates = {}
    
    if templates_dir.exists():
        for template_file in templates_dir.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template_data = json.load(f)
                    # Use the filename without extension as template name if not specified in the JSON
                    template_name = template_data.get("name", template_file.stem)
                    template_data["file_path"] = template_file
                    templates[template_name] = template_data
            except Exception as e:
                st.error(f"Error loading template {template_file}: {e}")
                
    return templates

# Function to save a template
def save_template(template_data):
    """Save a template to the templates directory"""
    templates_dir = Path("templates")
    
    # Create templates directory if it doesn't exist
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True)
    
    # Create a filename based on the template name
    filename = safe_filename(template_data["name"]) + ".json"
    file_path = templates_dir / filename
    
    with open(file_path, "w") as f:
        json.dump(template_data, f, indent=4)
    
    return file_path

# Function to delete a template
def delete_template(file_path):
    """Delete a template file"""
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        st.error(f"Error deleting template: {e}")
        return False

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

    st.title("Template Manager")

    if st.button("Back", use_container_width=True):
        st.switch_page("app.py")
    
    # Initialize session state for tracking template creation/deletion
    if 'template_action_done' not in st.session_state:
        st.session_state.template_action_done = False
        st.session_state.template_action_message = ""
    
    # Initialize all form field session states if they don't exist
    if 'template_name' not in st.session_state:
        st.session_state.template_name = ""
    if 'template_script_type' not in st.session_state:
        st.session_state.template_script_type = "py"
    if 'template_script_content' not in st.session_state:
        st.session_state.template_script_content = ""
    if 'template_interval_value' not in st.session_state:
        st.session_state.template_interval_value = 1
    if 'template_interval_unit' not in st.session_state:
        st.session_state.template_interval_unit = "minutes"
    if 'template_enabled' not in st.session_state:
        st.session_state.template_enabled = False
    
    # Check if we need to reset the form
    if 'reset_template_form' not in st.session_state:
        st.session_state.reset_template_form = False
    
    # Reset form if flag is set
    if st.session_state.reset_template_form:
        st.session_state.template_name = ""
        st.session_state.template_script_type = "py"
        st.session_state.template_script_content = ""
        st.session_state.template_interval_value = 1
        st.session_state.template_interval_unit = "minutes"
        st.session_state.template_enabled = False
        st.session_state.reset_template_form = False
    
    # Show success/info message when template was created or deleted
    if st.session_state.template_action_done:
        st.success(st.session_state.template_action_message)
        st.session_state.template_action_done = False
        
    # Create tabs for different template actions
    tab1, tab2 = st.tabs(["View Templates", "Create Template"])

    with tab1:
        # Load and display templates
        templates = load_templates()
        
        if not templates:
            st.info("No templates found.")
        else:
            st.write(f"Found {len(templates)} templates:")
            
            for template_name, template_data in templates.items():
                with st.expander(template_name):
                    # Handle possible typos in the key names from the JSON
                    script_type = template_data.get('script-type', 'py')
                    interval = template_data.get('interval', template_data.get('inteval', 1))
                    interval_unit = template_data.get('interval-unit', template_data.get('intertval-unit', 'minutes'))
                    enabled = template_data.get('enabled', False)
                    script_content = template_data.get('script-content', '')
                    
                    st.markdown(f"**Script Type:** {script_type}")
                    st.markdown(f"**Interval:** {interval} {interval_unit}")
                    st.markdown(f"**Enabled by default:** {enabled}")
                    
                    # Show/hide script content
                    show_script = st.toggle("Show Script Content", key=f"toggle_{template_name}")
                    if show_script:
                        st.code(script_content, language=script_type)

                    
                    # Delete button
                    if st.button("Delete Template", key=f"delete_{template_name}"):
                        if delete_template(template_data["file_path"]):
                            st.session_state.template_action_done = True
                            st.session_state.template_action_message = f"Template '{template_name}' deleted successfully"
                            st.rerun()
    
    with tab2:
        # Form for creating a new template
        with st.form(key="add_template_form"):
            name = st.text_input("Template Name", value=st.session_state.template_name, key="template_name")
            
            script_type_options = ["py", "sh", "php", "js", "rb", "pl", "ps1", "bat", "cmd", "r", "lua", "go", "sql"]
            script_type = st.selectbox(
                "Script Type",
                options=script_type_options,
                index=script_type_options.index(st.session_state.template_script_type) if st.session_state.template_script_type in script_type_options else 0,
                key="template_script_type"
            )
            
            script_content = st.text_area(
                "Script Content", 
                value=st.session_state.template_script_content,
                height=300, 
                placeholder="Enter your code here...",
                key="template_script_content"
            ) 
            
            col1, col2 = st.columns(2)
            with col1:
                interval_value = st.number_input(
                    "Interval", 
                    min_value=1, 
                    value=st.session_state.template_interval_value,
                    key="template_interval_value"
                )
            
            with col2:
                interval_units = ["minutes", "hours", "days"]
                interval_unit = st.selectbox(
                    "Unit",
                    options=interval_units,
                    index=interval_units.index(st.session_state.template_interval_unit) if st.session_state.template_interval_unit in interval_units else 0,
                    key="template_interval_unit"
                )
            
            # Add the enabled/disabled toggle
            enabled = st.toggle(
                "Enabled by default", 
                value=st.session_state.template_enabled, 
                help="Set whether jobs created from this template are enabled by default",
                key="template_enabled"
            )
            
            # Submit button
            submit = st.form_submit_button("Create Template", use_container_width=True)
            
            if submit:
                if name and script_content:
                    # Create template data
                    template_data = {
                        "name": name,
                        "script-type": script_type,
                        "script-content": script_content,
                        "interval": interval_value,
                        "interval-unit": interval_unit,
                        "enabled": enabled
                    }
                    
                    # Save the template
                    save_template(template_data)
                    
                    # Set session state to indicate template was created
                    st.session_state.template_action_done = True
                    st.session_state.template_action_message = f"Template '{name}' created successfully"
                    
                    # Create a flag to reset the form on the next run
                    st.session_state.reset_template_form = True
                    
                    # Rerun the app to show the success message
                    st.rerun()
                else:
                    st.error("Provide a name and script content to create a template.")

# Run the page
if __name__ == "__main__":
    main()