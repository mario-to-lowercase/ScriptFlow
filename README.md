# TaskFlow  ![GitHub Repo stars](https://img.shields.io/github/stars/mario-to-lowercase/TaskFlow)

![Dashboard Preview](https://raw.githubusercontent.com/mario-to-lowercase/TaskFlow/refs/heads/master/assets/home.png)

**TaskFlow** is a simple UI-based tool that allows you to create and manage jobs (cron jobs) that execute provided scripts based on a given interval. Built with Streamlit, TaskFlow offers an intuitive interface for scheduling and monitoring your scripts with ease.

---

## 🌟 Features  

- **🖥️ User-Friendly Interface**  
  Create, edit, and delete scheduled jobs through an intuitive Streamlit-based UI.

- **📜 Multiple Script Support**  
  Run different scripts with customized execution intervals all from one central dashboard.

- **⏱️ Customizable Intervals**  
  Schedule scripts to run at specific times (minutes, hours, days).

- **📊 Log Tracking**  
  Monitor script execution results and track performance over time.

- **📝 Template Management**
  Create, view, and manage reusable templates for your jobs.

- **🚀 Lightweight and Efficient**  
  Small footprint with powerful scheduling capabilities.

- **🔄 Command-Line Arguments**
  Define default arguments and override them during manual execution.

- **🎯 Dedicated Run Interface**
  Execute any job on-demand with custom arguments through a dedicated page.

---

## 🛠️ Upcoming Features (Todo)  

- **API Integration**: Trigger scripts via HTTP requests.
- **Advanced Scheduling**: Support for more complex scheduling patterns.
- **Translations**: Support for multiple languages in the user interface.
- **Webhook Management**: Create, execute and manage webhooks for integration with external services.

---

## 📁 Project Structure

TaskFlow follows a modular organization for better maintainability and scalability:

### Core Components

* `app.py` - Entry point of the application that initializes the Streamlit interface and manages the overall workflow, now with argument handling capabilities

### Directories

* `/pages` - Contains individual Streamlit pages for different views and functionality
  * `1_jobs.py` - Displays and manages job listings with argument support
  * `2_add_job.py` - Form for creating new jobs with default arguments
  * `3_history.py` - Execution history with argument tracking
  * `4_templates.py` - Template management with default argument support
  * `5_run.py` - Dedicated page for executing jobs with custom arguments
  
* `/scripts` - Repository for all executable job scripts
  * Stores user-created scripts that get executed according to schedule
  
* `/templates` - Collection of reusable job templates
  * Pre-defined script templates that can be used as starting points for new jobs
  
* `/data` - Storage for application state and historical information
  * `jobs.json` - Maintains the current configuration of all created jobs including default arguments
  * `history.json` - Records comprehensive execution history with timestamps, results, and arguments used

---

## 🛠️ Installation  

1. Clone the repository:  
   ```bash
   git clone https://github.com/mario-to-lowercase/TaskFlow.git
   cd TaskFlow
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Start the application:  
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Getting Started  

1. Open the UI in your browser.
2. Click on "Add Job" to create a new script execution task.
3. Define a name for your job, select the script type, add your script content, and set the execution interval.
4. Add default arguments that will be passed to your script during execution.
5. Save the job to schedule automatic execution.
6. Use the "Run" page to execute jobs on-demand with custom arguments.
7. Monitor logs for execution history, errors, and arguments used.

---

## 🛠️ Configuration

TaskFlow's interface allows you to easily configure your script execution preferences:

- Define script execution intervals directly via the UI
- Set default command-line arguments for your scripts
- Override arguments during manual execution
- Manage active jobs and disable them when needed
- View execution logs with argument details directly within the application

---

## 🍓 Raspberry Pi Setup  

Ensure TaskFlow starts automatically when your Raspberry Pi boots up using `systemd` with these simple steps:

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/taskflow.service
   ```

2. Add the following content:  
   ```ini
   [Unit]
   Description=TaskFlow
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /home/pi/TaskFlow/app.py
   WorkingDirectory=/home/pi/TaskFlow
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

3. Save the file and reload `systemd`:  
   ```bash
   sudo systemctl daemon-reload
   ```

4. Enable the service to start on boot:  
   ```bash
   sudo systemctl enable taskflow
   ```

5. Start the service:  
   ```bash
   sudo systemctl start taskflow
   ```

6. Stop the service:  
   ```bash
   sudo systemctl stop taskflow
   ```

7. Check the status:  
   ```bash
   sudo systemctl status taskflow
   ```

---

## 🤝 Contributing  

We welcome contributions to improve TaskFlow! Follow these steps:  

1. Fork the repository.  
2. Create a new branch:  
   ```bash
   git checkout -b feature/new-feature
   ```  
3. Commit your changes:  
   ```bash
   git commit -m "Add a new feature"
   ```  
4. Push your branch:  
   ```bash
   git push origin feature/new-feature
   ```  
5. Submit a pull request for review.  

---

## 📜 License  

TaskFlow is released under the [MIT License](https://github.com/mario-to-lowercase/TaskFlow/blob/master/LICENSE).