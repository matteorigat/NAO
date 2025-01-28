import cv2

# Load the pre-trained Haar Cascade Classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the video capture object
cap = cv2.VideoCapture(0)  # Use 0 for the default webcam

# Initialize the tracker variable
tracker = None
tracking_face = False

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if not tracking_face:
        # Detect faces in the grayscale frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            # Select the first detected face (you can modify this to select a specific face)
            x, y, w, h = faces[0]
            tracker = cv2.TrackerCSRT_create()
            tracker.init(frame, (x, y, w, h))
            tracking_face = True
            print("Face detected and tracking started.")
    else:
        # Update the tracker
        success, bbox = tracker.update(frame)
        if success:
            # Draw a rectangle around the tracked face
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            tracking_face = False
            print("Lost track of the face. Re-detecting.")
            tracker = None

    # Display the resulting frame
    cv2.imshow('Face Tracking', frame)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()