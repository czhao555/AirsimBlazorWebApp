# ASP.NET Core Blazor FPV Drone Simulator Dashboard

## Overview
This project is an **ASP.NET Core Blazor** web application that integrates with the **AirSim FPV Drone Simulator**. 
The dashboard provides real-time drone telemetry, including GPS coordinates, speed, battery level, flight history, alerts, camera feed, and telemetry data. 
The goal is to create an interactive interface for drone simulation and data visualization.

## Features
- **Real-time Drone Telemetry**: Displays essential drone data like GPS position, altitude, speed, and battery status.
- **Flight History Tracking**: Logs past flights with timestamps and locations.
- **Camera Feed Streaming**: Streams FPV drone view from Unreal Engine to the Blazor dashboard.
- **Alerts & Notifications**: Displays warnings for battery level, GPS loss, or connection issues.
- **AirSim Integration**: Communicates with AirSim using PX4 and the AirSim API for drone control and telemetry data retrieval.
- **Customizable UI**: Interactive and responsive dashboard built with Blazor.

## Technologies Used
- **Frontend**: Blazor (ASP.NET Core)
- **Backend**: C# (ASP.NET Core Web API)
- **Simulator**: AirSim (Unreal Engine-based FPV drone simulator)
- **Communication**: PX4 controller, AirSim API (Command through python script)
- **Hosting**: Cloudflare (for tunneling), IIS (for hosting)

## Installation & Setup
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```
2. **Install Dependencies:**
   ```sh
   dotnet restore
   ```
3. **Run the Backend Server:**
   ```sh
   dotnet run
   ```
4. **Set Up AirSim:**
   - Ensure AirSim is installed and configured to communicate with PX4 and the AirSim API.
   - Modify `settings.json` to match your network configuration.
    
5. **Set Up PX4 controller:**
   - Ensure it can communicate with Airsim. Example: sending command and check status

6. **Run Python Script:**
   - The two Python scripts in the repository (\BlazorApp1\proxy) do not start automatically when the Blazor web application runs.
   - You need to manually execute these scripts to enable data communication, including frame streaming, drone commands, and telemetry data.
   - To run the scripts:
     Open CMD, navigate to the directory containing the Python files, and execute:
     ```sh
     python airsim_proxy.py
     python airsim1.py
       ```
   - To avoid running them manually each time, consider creating a BAT file for automation.

8. **Access the Dashboard:**
   - Open `https://localhost:PORT` in your browser.
   - Ensure the Blazor app connects successfully to AirSim.

## Configuration
- Modify **`appsettings.json`** to adjust connection settings.
- Change **PX4 communication ports** if needed to avoid conflicts.

## Current Improvement
- Streaming Method Update: Switched from frame-by-frame capture streaming to WebRTC for improved performance and lower latency.
- Improved Control Sensitivity: Adjusted input handling and response curves for more precise and smoother drone control, reducing latency and overshooting during maneuvering
- Optimized Network Communication: Improved data handling between AirSim and the Blazor dashboard.
- UI Enhancements: Refined dashboard design for better user experience and data visualization.


## Future Enhancements
- Add support for **multiple drones**.
- Implement **AI-based flight analysis**.
- Improve **3D visualization of flight paths**.

## License
This project is open-source under the **MIT License**.

## Contact
For any questions or contributions, reach out to **Choo Zhen Hao**.

