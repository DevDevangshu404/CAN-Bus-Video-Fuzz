# Devangshu Mazumder - 2685040 - MSc Cyber Security Project
# CAN Fuzzing Tool with Computer Vision and Video Detection

This project is a CAN (Controller Area Network) fuzzing tool that integrates video detection to identify vulnerabilities in automotive or industrial systems. The tool uses a GUI built with `Tkinter`, CAN communication via the `python-can` library, and video processing with `OpenCV`.

## Features

- **CAN Fuzzing:** Perform full-range or quick fuzzing on CAN IDs with the ability to ignore specific IDs. Ranged fuzzing logic is integrated as part of the full fuzzing logic, allowing you to specify a range of CAN IDs to fuzz.

- **Video Detection:** Detect visual changes in the environment using a connected camera, and correlate these changes with the CAN messages sent. The tool automatically recognizes and chooses the default camera for video capture.

- **Internal State Logging:** Detect and log internal state changes based on CAN messages received from the system after sending fuzzed messages.

- **GUI Interface:** A user-friendly interface allows you to start and monitor fuzzing, view the real-time video feed, and review logs of sent CAN messages and detected changes.

## Installation
Install Python and PIP:
sudo apt install python3 python3-pip -y

Install Tkinter for GUI:
sudo apt install python3-tk -y

Install CAN Utilities and SocketCAN Support
sudo apt install can-utils -y

Setup Canbus Interface
sudo ip link set can0 up type can bitrate 500000

or Similarly the command to install the required Python packages
sudo pip3 install -r requirements.txt

### Running the tool
python3 GUI_Fuzz.py


### After Running the script
Select Fuzzing Type:
 Full Fuzzing: Press 1                                                           Fuzz the entire range of CAN IDs.
 Quick Fuzzing: Press 2                                                          Similar to full fuzzing but with shorter delays for faster operation.
 Ranged Fuzzing: Press 3 and Specify a start and end CAN ID in hex eg: 0x280     This is processed within the full fuzzing logic.
   Specify CAN IDs:                                                              Enter the range of CAN IDs to fuzz and any IDs to ignore.
     Video Recording: yes/no                                                     Choose whether to record video clips when visual changes are detected.
     Monitor GUI:                                                                The GUI will display the video feed, logs of sent CAN messages, and detected changes.

### Prerequisites

- Python 3.7 or higher
- A system with `socketcan` support (e.g., Linux, specifically Ubuntu)
- A CAN interface (e.g., USB-to-CAN adapter)
- A camera connected to the system (for video detection)

### Ubuntu Setup

1. **Update and Upgrade the System:**
   ```bash
   sudo apt update
   sudo apt upgrade -y

## Video Detection Tips

### Camera Adjustment:
The video camera might need some physical adjustments for optimal detection. Ensure the camera is stable and properly positioned to capture the area of interest. Use lamp lighting if needed

### Threshold and Min Area Settings:
The best threshold and minimum area values found for detecting significant changes are `30` and `230` respectively. These values can be adjusted in the code if needed to suit different environments.
