import cv2
import mediapipe as mp
import numpy as np
import math
import tkinter as tk
from tkinter import ttk
import threading
import time

# Configuração do MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Classe para detecção da cabeça
class HeadDetector:
    def __init__(self, detection_confidence=0.7):
        self.pose = mp_pose.Pose(min_detection_confidence=detection_confidence)

    def detect_head_movement(self, image):
        # Converte a imagem para RGB (necessário para o MediaPipe)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
    
        if results.pose_landmarks:
            # Pegando os pontos dos ombros e nariz
            landmarks = results.pose_landmarks.landmark
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

            # Cálculo da inclinação horizontal
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
            horizontal_diff = nose.x - shoulder_center_x

            # Cálculo da inclinação vertical
            shoulder_center_y = (left_shoulder.y + right_shoulder.y) / 2
            vertical_diff = shoulder_center_y - nose.y
            print(f"vertical_diff: {vertical_diff:.4f}, horizontal_diff: {horizontal_diff:.4f}")
            if horizontal_diff > 0.05:
                     return "Direita"
            elif horizontal_diff < -0.05:
                  return "Esquerda"
            elif vertical_diff > 0.45:
                     return "Cima"
            elif vertical_diff < 0.4:
                     return "Baixo"
            else:
                 return "Centro"

                 return "Sem detecção"
            


# Classe da interface gráfica
class InterfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle por Cabeça")
        self.label = ttk.Label(root, text="Detectando...")
        self.label.pack(padx=10, pady=10)
        self.running = True
        self.head_detector = HeadDetector()

        # Thread da câmera
        self.capture_thread = threading.Thread(target=self.run_detection)
        self.capture_thread.start()

        # Botão para parar
        self.stop_button = ttk.Button(root, text="Parar", command=self.stop)
        self.stop_button.pack(padx=10, pady=5)

    def run_detection(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            direction = self.head_detector.detect_head_movement(frame)
            self.update_label(direction)

            # Exibe o frame com landmarks (opcional)
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.head_detector.pose.process(image_rgb)
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow("Webcam - Controle Cabeça", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def update_label(self, text):
        self.label.config(text=f"Movimento: {text}")

    def stop(self):
        self.running = False
        self.root.quit()

# Início do programa
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfaceApp(root)
    root.mainloop()
