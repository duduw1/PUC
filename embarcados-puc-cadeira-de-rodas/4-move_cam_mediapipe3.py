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
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.7)

# === Configurações ===
max_speed = 3.0
min_speed = 0.3
speed_gain = 4.0    # controle da sensibilidade vertical
turn_gain = 2.0     # controle da sensibilidade lateral

# === Estado de movimento ===
moving_forward = False
current_speed = 0.0

# === Funções auxiliares ===
def calculate_forward_speed(vertical_diff):
    speed = (vertical_diff) * speed_gain
    return max(min_speed, min(speed, max_speed)) if speed > 0 else 0

def calculate_turn_factor(horizontal_diff):
    return np.clip(horizontal_diff * turn_gain, -1.0, 1.0)

# === Loop principal ===
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    horizontal_diff = vertical_diff = 0
    movement = "Parado"
    left_speed = right_speed = 0

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        nose = lm[mp_pose.PoseLandmark.NOSE]
        l_sh = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_sh = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        shoulder_cx = (l_sh.x + r_sh.x) / 2
        shoulder_cy = (l_sh.y + r_sh.y) / 2

        horizontal_diff = nose.x - shoulder_cx
        vertical_diff = shoulder_cy - nose.y

        turn_factor = calculate_turn_factor(horizontal_diff)

        if vertical_diff > 0.05:
            # Iniciar ou ajustar movimento para frente
            current_speed = calculate_forward_speed(vertical_diff)
            left_speed = current_speed * (1 - turn_factor)
            right_speed = current_speed * (1 + turn_factor)
            moving_forward = True
            movement = "Frente com curva" if abs(turn_factor) > 0.1 else "Frente"
        elif moving_forward and abs(horizontal_diff) > 0.05:
            # Mantém velocidade, apenas curva
            left_speed = current_speed * (1 - turn_factor)
            right_speed = current_speed * (1 + turn_factor)
            movement = "Curvando..."
        elif abs(horizontal_diff) > 0.05:
            # Gira parado
            left_speed = -1.5 * np.sign(horizontal_diff)
            right_speed = 1.5 * np.sign(horizontal_diff)
            moving_forward = False
            current_speed = 0.0
            movement = "Girando parado"
        else:
            # Parado
            left_speed = right_speed = 0
            current_speed = 0.0
            moving_forward = False
            movement = "Parado"

        send_coppelia_command(round(left_speed, 2), round(right_speed, 2))

        # === Desenho dos landmarks (opcional) ===
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # === Overlay ===
    cv2.putText(frame, f"Movimento: {movement}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) if movement != "Parado" else (0, 255, 0), 2)
    if movement.startswith("Frente"):
        cv2.arrowedLine(frame, (w//2, h-40), (w//2, h-100), (0, 0, 255), 6)
        if turn_factor < -0.1:
            cv2.putText(frame, "←", (w//2 - 80, h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        elif turn_factor > 0.1:
            cv2.putText(frame, "→", (w//2 + 40, h//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    elif "Girando" in movement:
        arrow = "↺" if horizontal_diff < 0 else "↻"
        cv2.putText(frame, arrow, (w//2 - 40, h//2), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
    else:
        cv2.circle(frame, (w//2, h - 40), 15, (0, 255, 0), -1)

    cv2.imshow("Controle Natural de Cadeira", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sim.simxFinish(clientID)
