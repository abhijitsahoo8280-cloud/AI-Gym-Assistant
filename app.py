import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Gym Assistant", layout="wide")

# --- FUNCTIONS ---
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    return 360-angle if angle > 180.0 else angle

# --- MAIN UI ---
st.title(" AI Gym & Fitness Assistant")

menu = ["AI Gym Trainer", "AI Dietician"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "AI Gym Trainer":
    st.subheader("Bicep Curl Counter")
    run = st.checkbox('Start Camera')
    FRAME_WINDOW = st.image([])
    
    # Initialize variables in session state to prevent resetting
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
        st.session_state.stage = None

    camera = cv2.VideoCapture(1)
    mp_pose = mp.solutions.pose
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while run:
            ret, frame = camera.read()
            if not ret: break
            
            # Process Frame
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                
                angle = calculate_angle(shoulder, elbow, wrist)

                if angle > 160: st.session_state.stage = "down"
                if angle < 30 and st.session_state.stage == 'down':
                    st.session_state.stage = "up"
                    st.session_state.counter += 1
            except: pass

            # Draw Reps on Image
            cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
            cv2.putText(image, str(st.session_state.counter), (10,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
            
            FRAME_WINDOW.image(image, channels="BGR")
        camera.release()

elif choice == "AI Dietician":
    st.subheader("AI Diet Planner")
    w = st.number_input("Weight (kg)", value=70)
    h = st.number_input("Height (cm)", value=170)
    goal = st.selectbox("Goal", ["Weight Loss", "Muscle Gain"])
    
    if st.button("Get Plan"):
        bmi = round(w / ((h/100)**2), 2)
        st.write(f"### Your BMI: {bmi}")
        if goal == "Weight Loss":
            st.success("Eat: Salads, Oats, Sprouts. Avoid: Sugar.")
        else:
            st.success("Eat: Eggs, Paneer, Chicken, Rice.")
            