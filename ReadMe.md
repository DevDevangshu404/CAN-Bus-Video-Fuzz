# Devangshu Mazumder - 2685040 - MSc Cyber Security Project
# **A New Frontier in Fuzzing: Real-Time Video Detection for CAN Bus Networks**

This project is a CAN (Controller Area Network) fuzzing tool that integrates video detection to identify vulnerabilities in automotive or industrial systems. The tool uses a GUI built with `Tkinter`, CAN communication via the `python-can` library, and video processing with `OpenCV`.

### Check more about it on my website: https://www.devangshumazumder.com/projects/content/videofuzz/fuzzing 

## Features

- **CAN Fuzzing:** Perform full-range or quick fuzzing on CAN IDs with the ability to ignore specific IDs. Ranged fuzzing logic is integrated as part of the full fuzzing logic, allowing you to specify a range of CAN IDs to fuzz.

- **Video Detection:** Detect visual changes in the environment using a connected camera, and correlate these changes with the CAN messages sent. The tool automatically recognizes and chooses the default camera for video capture.

- **Internal State Logging:** Detect and log internal state changes based on CAN messages received from the system after sending fuzzed messages.

- **GUI Interface:** A user-friendly interface allows you to start and monitor fuzzing, view the real-time video feed, and review logs of sent CAN messages and detected changes.

## Installation(Linux)

1.Install Python and PIP:

```bash
sudo apt install python3 python3-pip -y
```

2.Install Tkinter for GUI:

```bash
sudo apt install python3-tk -y
```

3.Install CAN Utilities and SocketCAN Support

```bash
sudo apt install can-utils -y
```

4.Setup Canbus Interface

```bash
sudo ip link set can0 up type can bitrate 500000
```

5. or Similarly the command to install the required Python packages

```bash
sudo pip3 install -r requirements.txt
```

### Running the tool

```bash
python3 GUI_Fuzz.py
```

### After Running the script
- Select Fuzzing Type:
-- Full Fuzzing: Press 1 (Fuzz the entire range of CAN IDs.)
-- Quick Fuzzing: Press 2 (Similar to full fuzzing but with shorter delays for faster operation.)
-- Ranged Fuzzing: Press 3 and Specify a start and end CAN ID in hex eg: 0x280 (This is processed within the full fuzzing logic.)
- Enter the range of CAN IDs to fuzz and any IDs to ignore: (Can Press Enter if you do not want to ignore)
- Video Recording: yes/no (Choose whether to record video clips when visual changes are detected)
- Monitor GUI: The GUI will display the video feed, logs of sent CAN messages, and detected changes.

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

## Reverse Engineered CAN Messages

| **CAN ID**  | **Data Position**      | **Effect Identified with Video Detection**                                                                              |
|-------------|------------------------|------------------------------------------------------------------------------------------------------------------------|
| **0x050**   | Byte 0, Byte 1          | Triggers both the seatbelt warning and power steering warning. Generates new traffic from CAN IDs 0x320 and 0x62F.     |
| **0x1A0**   | Byte 1, Bits 0, 1       | Activates the Electronic Stability Control (ESC) warning when Bit 1 is set to 1, and deactivates ABS warning with Bit 0. |
| **0x280**   | Byte 3                  | Adjusts the **tachometer gauge (RPM)** based on the value between 0h and 60h.                                           |
| **0x343**   | Byte 2                  | Activates the tire pressure monitoring warning when set to **FF**.                                                      |
| **0x361**   | Entire Message          | Generates new traffic from CAN ID 0x625.                                                                                |
| **0x373**   | Entire Message          | Activates the power steering warning light and causes unexpected behavior on the display below the mileage indicator.    |
| **0x3D0**   | Byte 1                  | Controls the power steering warning light (Bit 1 for amber light, remaining for red light).                              |
| **0x470**   | Byte 0, Byte 1          | Byte 0: Triggers car battery warning. Byte 1: Wakes up open door alarm. Controls additional alarms for boot and exterior lights. |
| **0x531**   | Byte 0, Byte 1, Byte 2  | Byte 0: Controls main beam caution lamp, rear fog caution lamp. Byte 2: Activates additional indicators.                 |
| **0x540**   | Byte 0                  | Displays the **"P R N D 4 3 2" sequence** on the center screen, related to gearbox indication.                          |
| **0x5C0**   | Byte 5, Byte 6          | Byte 5: Controls brake pedal illumination. Byte 6: Controls electronic parking brake illumination.                      |
| **0x5D0**   | Byte 0                  | Causes abnormality in mileage reading.                                                                                  |


