

# 🧑‍🏫 Smart Real-Time Face Recognition Attendance System

This Python application is a real-time attendance system that uses a webcam to recognize individuals, record their attendance time, and automatically log the data into a Google Sheet spreadsheet.

It features persistent storage for known faces and an interactive mode to register unknown faces on the fly.

## ✨ Features

  * **Real-Time Face Recognition:** Uses the highly accurate `face_recognition` library (based on dlib's state-of-the-art model) for rapid identification.
  * **Google Sheets Integration:** Automatically logs attendance records (Name, Roll Number, Time, Section) to a specified Google Sheet using the `google-api-python-client`.
  * **Persistent Storage:** Known face encodings and metadata are saved locally as JSON files in the `known_faces` directory, ensuring the system remembers individuals across sessions.
  * **On-the-Fly Enrollment:** Allows the operator to register an `Unknown` person by pressing **`7`** when the face is detected. This saves their encoding locally and records their first attendance immediately.
  * **Single Entry Rule:** Prevents duplicate attendance records by only writing a recognized person's details to the sheet once per session.
  * **Visual Feedback:** Draws green bounding boxes for known faces and red bounding boxes for unknown faces.

## 🛠️ Prerequisites

### 1\. Python and Libraries

This project requires Python 3.6+ and the following libraries. The `face_recognition` library has a dependency on `dlib`, which can sometimes require specific build tools on your system (e.g., CMake).

```bash
# Core libraries
pip install opencv-python numpy face-recognition

# Google Sheets API libraries
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2\. Google Sheets API Setup

The application needs authorization to access and edit your Google Sheet.

1.  **Enable the API:**
      * Go to the [Google Cloud Console] and enable the **Google Sheets API** for your project.
2.  **Create Service Account:**
      * In the Google Cloud Console, navigate to **IAM & Admin** -\> **Service Accounts**.
      * Create a new Service Account. Grant it the **Owner** or **Editor** role (or a specific role that includes Sheets API permissions).
3.  **Download Credentials:**
      * After creating the service account, click the three dots under **Actions** and select **Manage Keys** -\> **Add Key** -\> **Create new key** -\> **JSON**.
      * This downloads the credentials file (e.g., `probable-gizmo-422809-j3-5a586f51c4fb.json`).
4.  **Share the Sheet:**
      * Open your target Google Sheet.
      * Share the spreadsheet with the **email address of the Service Account** you just created (e.g., `your-service-account-name@your-project-id.iam.gserviceaccount.com`). Grant it **Editor** access.

## ⚙️ Configuration

Before running, update the following global variables in the script:

| Variable | Description |
| :--- | :--- |
| `SERVICE_ACCOUNT_FILE` | **Crucial:** Must match the name of the JSON file you downloaded from Google Cloud. |
| `SPREADSHEET_ID` | Replace `'1yoRDXduvNPiIKEynRXCBkxnU5huywfpipQiM4th5tyc'` with the ID from your spreadsheet's URL. |

### Font Dependency

The helper function `add_text_to_image` attempts to use the `arial.ttf` font. If this is not found on your system, the script will fall back to a default font.

## 🚀 How to Run

1.  **Preparation:** Ensure all dependencies are installed and the Google Sheets configuration is complete. Place the service account JSON file and the Python script in the same directory.

2.  **Execute the Script:**

    ```bash
    python attendance_system.py
    ```

3.  **Operation:**

      * The webcam feed will open.
      * **Known Faces:** If a known face is detected (green box), their attendance is logged to the Google Sheet automatically (once per session).
      * **Unknown Faces:** If an unknown face is detected (red box with "Unknown" label), you have the option to enroll them.

### On-the-Fly Enrollment

1.  Ensure the unknown face is visible on screen.
2.  Press the **`7`** key on your keyboard.
3.  The console will prompt you to enter the person's details:
      * `Enter name:`
      * `Enter roll number:`
      * `Enter section:`
4.  Once entered, the person is immediately registered in the `known_faces` directory and their attendance is logged.

### Exit

Press the **`q`** key to stop the camera and close the application.

## 📂 Project Structure

```
.
├── attendance_system.py             # Main script
├── probable-gizmo-422809-j3-5a586f51c4fb.json # Service Account Key
└── known_faces/
    ├── John_Doe.json                # Stored face encoding and metadata
    ├── Jane_Smith.json              # Stored face encoding and metadata
    └── ...
```
