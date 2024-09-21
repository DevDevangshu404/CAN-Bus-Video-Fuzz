import tkinter as tk
from tkinter import ttk
import cv2
import can
import time
import threading


class CANFuzzingTool:
    def __init__(self, root, start_id, end_id, ignore_ids, fuzz_type, record_video):
        self.root = root
        self.root.title("VIDEO DETECTION CAN Fuzzing Tool")
        self.setup_ui()  # Sets up the GUI elements

        # Initializes parameters for CAN fuzzing
        self.start_id = start_id
        self.end_id = end_id
        self.ignore_ids = ignore_ids
        self.fuzz_type = fuzz_type
        self.record_video = record_video

        # Sets up CAN interface using socketcan
        self.can_interface = "can0"
        self.bus = can.interface.Bus(self.can_interface, bustype="socketcan")

        # Setup for video capture using OpenCV
        self.cap = cv2.VideoCapture(0)  # Use the default camera
        self.prev_frame = None
        self.output_file = None
        self.recording = False

        # Variables to store the last CAN ID and data for logging purposes
        self.current_can_id = None
        self.current_data = None

        # Starts fuzzing in a separate thread to keep the GUI responsive
        self.fuzzing_thread = threading.Thread(target=self.start_fuzzing)
        self.fuzzing_thread.daemon = True
        self.fuzzing_thread.start()

        # Starts updating the video feed in the GUI
        self.update_video_feed()

    # Function to set up the user interface (UI)
    def setup_ui(self):
        # Create frames for video, message panel, and log display
        self.video_frame = ttk.Frame(self.root)
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.message_panel = ttk.Frame(self.root)
        self.message_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.log_frame = ttk.Frame(self.root)
        self.log_frame.grid(
            row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2
        )

        # Video feed label to display the camera feed
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.grid(row=0, column=0)

        # Label for visual and internal state change logs
        self.visual_triggered_label = ttk.Label(
            self.message_panel, text="Visual & Internal State Changes"
        )
        self.visual_triggered_label.grid(row=0, column=0, pady=5)

        # Listbox to display messages related to visual and internal state changes
        self.messages_listbox = tk.Listbox(self.message_panel, height=25)
        self.messages_listbox.grid(row=1, column=0, sticky="nsew")

        # Label for displaying all sent CAN messages
        self.triggered_message_label = ttk.Label(
            self.message_panel, text="All Sent CAN Messages"
        )
        self.triggered_message_label.grid(row=2, column=0, pady=5)

        # Textbox to display logs of all sent CAN messages
        self.triggered_message_display = tk.Text(self.message_panel, height=8)
        self.triggered_message_display.grid(row=3, column=0, sticky="nsew")

    # Function to start fuzzing based on the selected fuzzing type
    def start_fuzzing(self):
        if self.fuzz_type == "full":
            self.fuzz_ids(
                self.start_id, self.end_id, self.ignore_ids
            )  # Full range fuzzing
        elif self.fuzz_type == "quick":
            self.quick_fuzz_ids(
                self.start_id, self.end_id, self.ignore_ids
            )  # Quick fuzzing with shorter delays

    # Function for full range fuzzing
    def fuzz_ids(self, start_id, end_id, ignore_ids):
        for can_id in range(start_id, end_id + 1):
            if can_id in ignore_ids:  # Skip ignored CAN IDs
                continue

            for i in range(8):  # Fuzz each byte in the data field
                for data_byte in range(256):
                    data = [0x00] * 8
                    data[i] = data_byte  # Modify one byte at a time
                    self.send_can_message(can_id, data)  # Send the CAN message
                    time.sleep(0.1)  # Delay to avoid overwhelming the bus

    # Function for quick fuzzing with shorter delays
    def quick_fuzz_ids(self, start_id, end_id, ignore_ids):
        for can_id in range(start_id, end_id + 1):
            if can_id in ignore_ids:
                continue

            for i in range(8):
                for data_byte in range(256):
                    data = [0x00] * 8
                    data[i] = data_byte
                    self.send_can_message(can_id, data)
                    time.sleep(0.05)  # Shorter delay for quicker fuzzing

    # Function to send a CAN message
    def send_can_message(self, arbitration_id, data):
        try:
            # Create a CAN message
            message = can.Message(
                arbitration_id=arbitration_id, data=data, is_extended_id=False
            )
            self.bus.send(message)  # Send the message on the CAN bus
            self.current_can_id = arbitration_id  # Store the CAN ID for logging
            self.current_data = data  # Store the data for logging

            # Log the sent message
            self.root.after(0, lambda: self.log_sent_message(arbitration_id, data))

            # Check for internal state changes
            self.check_internal_state_change()

        except can.CanOperationError as e:
            print(f"Error sending CAN message: {e}")  # Handle any errors during sending

    # Function to check for internal state changes after sending a CAN message
    def check_internal_state_change(self):
        try:
            # Read a message from the CAN bus (non-blocking)
            message = self.bus.recv(timeout=0.1)
            if message is not None:
                # Process and log the received message as an internal state change
                self.log_internal_state_change(message)
        except can.CanOperationError as e:
            print(f"Error reading CAN message: {e}")

    # Function to log detected internal state changes to a file
    def log_internal_state_change(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_text = f"{timestamp} - Received CAN ID: {hex(message.arbitration_id)}, Data: {[hex(byte) for byte in message.data]}"
        log_filename = "can_log.txt"
        with open(log_filename, "a") as log_file:
            log_file.write(f"[INTERNAL STATE] {log_text}\n")

    # Function to update the video feed in the GUI
    def update_video_feed(self):
        ret, frame = self.cap.read()  # Capture a frame from the camera
        if ret:
            if self.prev_frame is None:
                self.prev_frame = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2GRAY
                )  # Convert the first frame to grayscale

            # Process the captured frame
            processed_frame = self.process_frame(frame)

            # Convert BGR to RGB format for display
            img_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            img_rgb = cv2.resize(img_rgb, (640, 480))  # Resize to fit the GUI

            # Convert the processed image to Tkinter PhotoImage
            img_tk = self.convert_to_tk(img_rgb)
            self.video_label.imgtk = img_tk
            self.video_label.configure(image=img_tk)  # Update the image in the GUI

            # Record the video if recording is enabled
            if self.recording and self.output_file is not None:
                self.output_file.write(
                    processed_frame
                )  # Write the processed frame to the video file

        # Schedule the next video feed update
        self.root.after(10, self.update_video_feed)

    # Convert the processed frame to a format suitable for Tkinter
    def convert_to_tk(self, img):
        img_pil = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB format
        return tk.PhotoImage(
            master=self.video_label,
            width=img.shape[1],
            height=img.shape[0],
            data=cv2.imencode(".ppm", img_pil)[1].tobytes(),
        )

    # Function to process each frame and detect visual changes
    def process_frame(self, frame):
        gray_frame = cv2.cvtColor(
            frame, cv2.COLOR_BGR2GRAY
        )  # Convert frame to grayscale
        contours = self.detect_changes(
            self.prev_frame, gray_frame
        )  # Detect changes between frames
        self.prev_frame = gray_frame.copy()  # Update previous frame

        change_detected = False

        # Draw rectangles around detected changes
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 230:  # Only consider significant changes
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                change_detected = True

        # If a change is detected, log the corresponding CAN message
        if (
            change_detected
            and self.current_can_id is not None
            and self.current_data is not None
        ):
            self.root.after(
                0,
                lambda: self.log_triggered_message(
                    self.current_can_id, self.current_data
                ),
            )

            # Start recording if not already recording
            if self.record_video and not self.recording:
                self.start_recording()

        # Stop recording if no changes are detected
        elif self.recording:
            self.stop_recording()

        return frame

    # Function to detect changes between the previous and current frames
    def detect_changes(self, prev_frame, curr_frame):
        diff = cv2.absdiff(  # Compute the absolute difference between frames
            prev_frame, curr_frame
        )
        _, thresh = cv2.threshold(  # Apply a binary threshold
            diff, 31, 255, cv2.THRESH_BINARY
        )
        dilated = cv2.dilate(  # Dilate the thresholded image to fill gaps
            thresh, None, iterations=2
        )
        contours, _ = cv2.findContours(
            dilated,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,  # Find contours of the changes
        )
        return contours

    # Function to start recording the video
    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Define the codec
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        video_filename = f"can_{hex(self.current_can_id)}_{'_'.join([hex(b) for b in self.current_data])}.avi"  # Define the filename based on the CAN ID and data
        self.output_file = (
            cv2.VideoWriter(  # Create a VideoWriter object to save the video
                video_filename, fourcc, 20.0, (frame_width, frame_height)
            )
        )
        self.recording = True
        print("Started recording...")

    # Function to stop recording the video
    def stop_recording(self):
        if self.output_file is not None:
            self.output_file.release()  # Release the VideoWriter object
            self.output_file = None
            self.recording = False
            print("Stopped recording.")

    # Function to log all sent CAN messages in the GUI
    def log_sent_message(self, can_id, data):
        timestamp = time.strftime("%H:%M:%S")  # Get the current time
        log_text = (
            f"{timestamp} - CAN ID: {hex(can_id)}, Data: {[hex(byte) for byte in data]}"
        )
        self.triggered_message_display.insert(  # Display the log in the text widget
            tk.END, log_text + "\n"
        )
        self.triggered_message_display.see(  # Scroll to the end of the text widget
            tk.END
        )

    # Function to log triggered messages (associated with visual changes)
    def log_triggered_message(self, can_id, data):
        timestamp = time.strftime("%H:%M:%S")
        log_text = (
            f"{timestamp} - CAN ID: {hex(can_id)}, Data: {[hex(byte) for byte in data]}"
        )
        self.messages_listbox.insert(tk.END, log_text)  # Display the log in the listbox
        self.messages_listbox.see(tk.END)

        # Also log the triggered message to a file
        log_filename = "can_log.txt"
        with open(log_filename, "a") as log_file:
            log_file.write(f"[VISUAL] {log_text}\n")


# Main execution starts here
if __name__ == "__main__":
    # Prompt the user to choose a fuzzing type
    fuzz_type = input(
        "Choose fuzzing type: 1) Full Fuzzing 2) Quick Fuzzing 3) Ranged Fuzzing: "
    )

    # Set the start and end CAN IDs based on the chosen fuzzing type
    if fuzz_type == "1":
        start_id = 0x000
        end_id = 0x7DF
        fuzz_type_str = "full"
    elif fuzz_type == "2":
        start_id = 0x000
        end_id = 0x7DF
        fuzz_type_str = "quick"
    elif fuzz_type == "3":
        start_id = int(input("Enter start CAN ID (hex): "), 16)
        end_id = int(input("Enter end CAN ID (hex): "), 16)
        fuzz_type_str = "full"
    else:
        print("Invalid option. Exiting.")
        exit()

    # Prompt the user to enter CAN IDs to ignore
    ignore_ids_input = input(
        "Enter CAN IDs to ignore (comma-separated, hex, e.g., 0x123, 0x456), or leave empty: "
    ).strip()
    ignore_ids = (
        [int(can_id.strip(), 16) for can_id in ignore_ids_input.split(",")]
        if ignore_ids_input
        else []
    )

    # Ask the user if they want to record video of visual changes
    record_video = (
        input("Do you want to record video clips of visual changes? (yes/no): ")
        .strip()
        .lower()
        == "yes"
    )

    # Initialize the Tkinter root window
    root = tk.Tk()
    root.geometry("1200x800")  # Set the size of the window
    # Create an instance of the CANFuzzingTool class with the specified parameters
    app = CANFuzzingTool(
        root, start_id, end_id, ignore_ids, fuzz_type_str, record_video
    )
    root.mainloop()  # Start the Tkinter event loop
