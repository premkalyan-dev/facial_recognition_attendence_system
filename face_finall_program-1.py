import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import face_recognition
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json

# Directory to save known face encodings and details
KNOWN_FACES_DIR = "known_faces"
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'probable-gizmo-422809-j3-5a586f51c4fb.json'  # Ensure this file is in the correct path

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of the spreadsheet
SPREADSHEET_ID = '1yoRDXduvNPiIKEynRXCBkxnU5huywfpipQiM4th5tyc'  # Replace with your actual spreadsheet ID
RANGE_NAME = 'Sheet1!A1:D1'

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# Load known faces
known_face_encodings = []
known_face_names = []
known_face_roll_numbers = {}
known_face_section = {}

def load_known_faces():
    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(KNOWN_FACES_DIR, filename), 'r') as f:
                face_data = json.load(f)
                known_face_encodings.append(np.array(face_data["encoding"]))
                known_face_names.append(face_data["name"])
                known_face_roll_numbers[face_data["name"]] = face_data["roll_number"]
                known_face_section[face_data["name"]] = face_data["section"]

def save_unknown_face(encoding, name, roll_number, section):
    face_data = {
        "encoding": encoding.tolist(),
        "name": name,
        "roll_number": roll_number,
        "section": section
    }
    filename = os.path.join(KNOWN_FACES_DIR, f"{name}.json")
    with open(filename, 'w') as f:
        json.dump(face_data, f)

load_known_faces()

# List to keep track of names already written to the Google Sheet
written_names = []

# Add header row to Google Sheets
try:
    header_row = [['Name', 'Roll Number', 'Time', 'Section']]
    sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
                          valueInputOption="RAW", body={"values": header_row}).execute()
    print("Header row added to Google Sheets.")
except Exception as e:
    print(f"Error adding header row: {e}")

def add_text_to_image(image, text, position):
    # Convert the image from OpenCV to PIL format
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # Use a truetype font
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Add text to image
    draw.text(position, text, font=font, fill=(255, 255, 255, 0))

    # Convert back to OpenCV format
    image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    return image_cv

def process_frame(image):
    # Convert the captured image to RGB (face_recognition uses RGB)
    rgb_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Find all face locations and encodings in the captured image
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    unknown_detected = False

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

            roll_number = known_face_roll_numbers[name]
            section = known_face_section[name]
            #user_info = f"{name}, {roll_number}, {section}" # You can use this if you need more info in the future

            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if name not in written_names:
                data_row = [[name, roll_number, time_now, section]]
                try:
                    sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
                                          valueInputOption="RAW", body={"values": data_row}).execute()
                    written_names.append(name)
                    print(f"Data for {name} written to Google Sheets.")
                except Exception as e:
                    print(f"Error writing data to Google Sheets: {e}")

            # Draw rectangle around the face
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(image, name, (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        else:
            unknown_detected = True
            unknown_face_encoding = face_encoding

            # Draw rectangle around the unknown face
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(image, name, (left, bottom + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return image, unknown_detected, unknown_face_encoding if unknown_detected else None

def main():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    print("Press 'q' to quit.")
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Process the frame
        frame, unknown_detected, unknown_face_encoding = process_frame(frame)

        # Display the resulting frame
        cv2.imshow('Face Recognition', frame)

        # Wait for key press
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            # If 'q' is pressed, exit the loop
            break
        elif unknown_detected and key == ord('7'):
            print("Unknown person detected. Please enter their details.")
            unknown_name = input("Enter name: ")
            unknown_roll_number = input("Enter roll number: ")
            unknown_section = input("Enter section: ")

            save_unknown_face(unknown_face_encoding, unknown_name, unknown_roll_number, unknown_section)
            known_face_encodings.append(unknown_face_encoding)
            known_face_names.append(unknown_name)
            known_face_roll_numbers[unknown_name] = unknown_roll_number
            known_face_section[unknown_name] = unknown_section

            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_row = [[unknown_name, unknown_roll_number, time_now, unknown_section]]
            try:
                sheet.values().append(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
                                      valueInputOption="RAW", body={"values": data_row}).execute()
                print(f"Data for {unknown_name} written to Google Sheets.")
            except Exception as e:
                print(f"Error writing data to Google Sheets: {e}")

            # Save the image
            cv2.imwrite('captured_image_with_name.jpg', frame)
            print("Image saved as 'captured_image_with_name.jpg'.")

    # Release the camera and close any open windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
