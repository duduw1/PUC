import cv2
import mediapipe as mp
import numpy as np
import time
import sys

# === Conexão com CoppeliaSim ===
try:
    import sim
except Exception as e:
    print("Erro ao importar sim:", e)
    sys.exit(1)

def initialize_coppelia():
    sim.simxFinish(-1)
    clientID = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
    if clientID != -1:
        print("Conectado ao CoppeliaSim")
        return clientID
    else:
        print("Erro ao conectar ao CoppeliaSim")
        sys.exit(1)

clientID = initialize_coppelia()

def send_coppelia_command(left_wheel_speed, right_wheel_speed):
    command_str = f"{left_wheel_speed},{right_wheel_speed}"
    sim.simxSetStringSignal(clientID, 'wheelchair_command', command_str, sim.simx_opmode_oneshot)
    print(f"Comando enviado: {command_str}")

# === MediaPipe ===
mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(min_detection_confidence=0.7)
face_mesh = mp_face.FaceMesh(refine_landmarks=True)

# === EAR para piscada ===
def euclidean(pt1, pt2):
    return np.linalg.norm(np.array(pt1) - np.array(pt2))

def eye_aspect_ratio(landmarks, eye_indices):
    A = euclidean(landmarks[eye_indices[1]], landmarks[eye_indices[5]])
    B = euclidean(landmarks[eye_indices[2]], landmarks[eye_indices[4]])
    C = euclidean(landmarks[eye_indices[0]], landmarks[eye_indices[3]])
    ear = (A + B) / (2.0 * C)
    return ear

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
EAR_THRESHOLD = 0.2

# === Funções de controle ===
def calculate_speed(diff, max_thresh=0.25, max_speed=2.0):
    value = min(abs(diff), max_thresh)
    return round((value / max_thresh) * max_speed, 2)

# === Loop principal ===
cap = cv2.VideoCapture(0)
last_blink_time = 0
blink_cooldown = 1.0
blink_action = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Pose
    pose_results = pose.process(frame_rgb)
    horizontal_diff = vertical_diff = 0
    movement = "Parado"
    left_speed = right_speed = 0

    if pose_results.pose_landmarks:
        lm = pose_results.pose_landmarks.landmark
        nose = lm[mp_pose.PoseLandmark.NOSE]
        l_sh = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_sh = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        shoulder_cx = (l_sh.x + r_sh.x) / 2
        shoulder_cy = (l_sh.y + r_sh.y) / 2

        horizontal_diff = nose.x - shoulder_cx
        vertical_diff = shoulder_cy - nose.y

    # Face
    face_results = face_mesh.process(frame_rgb)
    blink_now = time.time()
    if face_results.multi_face_landmarks:
        mesh = face_results.multi_face_landmarks[0]
        ih, iw = frame.shape[:2]
        points = [(int(lm.x * iw), int(lm.y * ih)) for lm in mesh.landmark]

        left_ear = eye_aspect_ratio(points, LEFT_EYE)
        right_ear = eye_aspect_ratio(points, RIGHT_EYE)

        # Desenha malha facial
        mp_drawing.draw_landmarks(frame, mesh, mp_face.FACEMESH_CONTOURS,
                                  mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                                  mp_drawing.DrawingSpec(color=(80,256,121), thickness=1))

        if right_ear < EAR_THRESHOLD and blink_now - last_blink_time > blink_cooldown:
            blink_action = "Girar Direita"
            last_blink_time = blink_now
        elif left_ear < EAR_THRESHOLD and blink_now - last_blink_time > blink_cooldown:
            blink_action = "Girar Esquerda"
            last_blink_time = blink_now
        else:
            blink_action = None

    # === Lógica de movimento ===
    if blink_action == "Girar Direita":
        send_coppelia_command(2.0, -2.0)
        movement = "Girar Direita"
    elif blink_action == "Girar Esquerda":
        send_coppelia_command(-2.0, 2.0)
        movement = "Girar Esquerda"
    elif horizontal_diff > 0.05:
        speed = calculate_speed(horizontal_diff)
        send_coppelia_command(speed, speed / 2)
        movement = "Frente Direita"
    elif horizontal_diff < -0.05:
        speed = calculate_speed(horizontal_diff)
        send_coppelia_command(speed / 2, speed)
        movement = "Frente Esquerda"
    elif abs(vertical_diff) < 0.03:
        send_coppelia_command(0, 0)
        movement = "Parado"

    # === Overlay visual com setas e texto ===
    cv2.putText(frame, f"Movimento: {movement}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255) if movement != "Parado" else (0,255,0), 2)

    if movement == "Frente Direita":
        cv2.arrowedLine(frame, (w//2, h-50), (w//2 + 60, h-100), (0,0,255), 5)
    elif movement == "Frente Esquerda":
        cv2.arrowedLine(frame, (w//2, h-50), (w//2 - 60, h-100), (0,0,255), 5)
    elif movement == "Girar Direita":
        cv2.putText(frame, "↻", (w//2+80, h//2), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 5)
    elif movement == "Girar Esquerda":
        cv2.putText(frame, "↺", (w//2-120, h//2), cv2.FONT_HERSHEY_SIMPLEX, 3, (0,0,255), 5)
    else:
        cv2.circle(frame, (w//2, h-50), 10, (0,255,0), -1)

    cv2.imshow("Controle Cabeça + Piscada", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sim.simxFinish(clientID)
