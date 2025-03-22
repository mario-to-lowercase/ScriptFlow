# ScriptFlow  ![GitHub Repo stars](https://img.shields.io/github/stars/mario-to-lowercase/scriptflow)

![Dashboard Preview](https://raw.githubusercontent.com/mario-to-lowercase/ScriptFlow/refs/heads/master/assets/home.png)

**ScriptFlow** is a simple UI-based tool that allows you to create and manage jobs (cron jobs) that execute provided scripts based on a given interval. Built with Streamlit, ScriptFlow offers an intuitive interface for scheduling and monitoring your scripts with ease.

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

---

## 🛠️ Upcoming Features (Todo)  

- **API Integration**: Trigger scripts via HTTP requests.
- **Advanced Scheduling**: Support for more complex scheduling patterns.

---

## 🛠️ Installation  

1. Clone the repository:  
   ```bash
   git clone https://github.com/mario-to-lowercase/ScriptFlow.git
   cd ScriptFlow
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
4. Save the job to schedule automatic execution.
5. Monitor logs for execution history and errors.

---

## 🛠️ Configuration

ScriptFlow's interface allows you to easily configure your script execution preferences:

- Define script execution intervals directly via the UI
- Manage active jobs and disable them when needed
- View execution logs directly within the application

---

## 🍓 Raspberry Pi Setup  

Ensure ScriptFlow starts automatically when your Raspberry Pi boots up with these simple steps:

### 🖥️ Using `systemd`

1. Create a service file:  
   ```bash
   sudo nano /etc/systemd/system/scriptflow.service
   ```

2. Add the following content:  
   ```ini
   [Unit]
   Description=ScriptFlow
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /home/pi/ScriptFlow/app.py
   WorkingDirectory=/home/pi/ScriptFlow
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
   sudo systemctl enable scriptflow
   ```

5. Start the service:  
   ```bash
   sudo systemctl start scriptflow
   ```

6. Stop the service:  
   ```bash
   sudo systemctl stop scriptflow
   ```

7. Check the status:  
   ```bash
   sudo systemctl status scriptflow
   ```

---

## 🤝 Contributing  

We welcome contributions to improve ScriptFlow! Follow these steps:  

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

ScriptFlow is released under the [MIT License](https://github.com/mario-to-lowercase/ScriptFlow/blob/master/LICENSE).