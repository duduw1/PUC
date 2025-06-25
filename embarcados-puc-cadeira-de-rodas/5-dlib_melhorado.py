# Importação de bibliotecas necessárias para visão computacional, interface gráfica, controle e integração
import dlib
# Importação de bibliotecas necessárias para visão computacional, interface gráfica, controle e integração
import cv2
# Importação de bibliotecas necessárias para visão computacional, interface gráfica, controle e integração
import numpy as np
# Importação de bibliotecas necessárias para visão computacional, interface gráfica, controle e integração
import time
# Importação de bibliotecas necessárias para visão computacional, interface gráfica, controle e integração
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from threading import Thread
# Importação de bibliotecas necessárias para visão computacional, interface gráfica, controle e integração
import sys
from collections import deque
import os

# Adicione o caminho para a API do CoppeliaSim
sys.path.append('sim.py')  # Substitua pelo caminho real

# Importa a API do CoppeliaSim
try:
# Importação de bibliotecas necessárias para visão computacional, interface gráfica, controle e integração
    import sim
except Exception as e:
    print("Erro ao importar a API do CoppeliaSim:", e)
    sys.exit(1)

# Inicializa a conexão com o CoppeliaSim
def initialize_coppelia():
    sim.simxFinish(-1)  # Fecha conexões anteriores
# Inicia conexão com o simulador CoppeliaSim. Se falhar, o programa é encerrado.
    clientID = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)  # Conectar ao CoppeliaSim
    if clientID != -1:
        print("Conectado ao CoppeliaSim")
        return clientID
    else:
        print("Falha ao conectar ao CoppeliaSim")
        sys.exit(1)

clientID = initialize_coppelia()

# Função para enviar comando ao CoppeliaSim
def send_coppelia_command(left_wheel_speed, right_wheel_speed):
    try:
        # Criar uma string com os valores separados por vírgula
        command_str = f"{left_wheel_speed},{right_wheel_speed}"
        # Enviar o comando como sinal de string
# Envia comando para o CoppeliaSim com as velocidades das rodas.
        sim.simxSetStringSignal(clientID, 'wheelchair_command', command_str, sim.simx_opmode_oneshot)
        print(f"Comando enviado para CoppeliaSim: {command_str}")
    except Exception as e:
        print(f"Erro ao enviar comando para CoppeliaSim: {e}")

# Variáveis globais
initial_nose_y = None

# Filas para armazenar os últimos valores de pitch e yaw
pitch_values = deque(maxlen=5)  # Média móvel dos últimos 5 frames
yaw_values = deque(maxlen=5)

# Variáveis para detecção de piscadas
EAR_THRESHOLD = 0.20  # Limiar para detecção de piscada (ajuste conforme necessário)
CONSEC_FRAMES = 1     # Número mínimo de frames com EAR abaixo do limiar para contar como piscada
COUNTER = 0
TOTAL_BLINKS = 0
DOUBLE_BLINK_TIME = 1.0  # Tempo máximo entre duas piscadas para considerar como dupla piscada
last_blink_time = 0

# Variáveis para trava
is_locked = True  # Estado inicial: bloqueado
last_movement_time = None
LOCK_TIMEOUT = 25  # Tempo em segundos para reativar a trava após inatividade

# Função para calcular a Razão de Aspecto dos Olhos (EAR)
# Função que calcula a abertura dos olhos para detectar piscadas.
def calculate_EAR(eye):
    # Calcula a distância euclidiana entre os pontos verticais
    A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
    B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
    # Calcula a distância euclidiana entre os pontos horizontais
    C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
    # Calcula a EAR
    EAR = (A + B) / (2.0 * C)
    return EAR

# Função para calcular o pitch usando o nariz
# Função que calcula o movimento vertical da cabeça (pitch) usando a posição do nariz.
def calculate_pitch_using_nose(landmarks):
    global initial_nose_y
    nose = np.array(landmarks[30])

    if initial_nose_y is None:
        initial_nose_y = nose[1]
        print(f"Posição inicial do nariz Y: {initial_nose_y}")

    nose_displacement = initial_nose_y - nose[1]  # Invertido para que inclinar para frente seja positivo
    print(f"Deslocamento do nariz Y: {nose_displacement}")
    return nose_displacement

# Função para calcular o yaw (giro) usando os olhos
# Função que calcula o movimento de rotação da cabeça (yaw) usando os olhos.
def calculate_yaw_using_eyes(landmarks):
    left_eye = np.array(landmarks[36])
    right_eye = np.array(landmarks[45])
    eye_vector = right_eye - left_eye
    yaw_angle = np.degrees(np.arctan2(eye_vector[1], eye_vector[0]))
    print(f"Yaw Angle: {yaw_angle}")
    return yaw_angle

# Função para mapear valores de controle para nomes de direções
# Função que traduz valores de yaw/pitch para nomes compreensíveis (ex: avançando, virando).
def get_direction_names(yaw_control, pitch_control):
    # Determinar o nome para yaw_control
    if yaw_control <= -0.5:
        yaw_name = "Virando acentuadamente à esquerda"
    elif -0.5 < yaw_control <= -0.1:
        yaw_name = "Virando à esquerda"
    elif -0.1 < yaw_control < 0.1:
        yaw_name = "Em linha reta"
    elif 0.1 <= yaw_control < 0.5:
        yaw_name = "Virando à direita"
    elif yaw_control >= 0.5:
        yaw_name = "Virando acentuadamente à direita"
    else:
        yaw_name = "Indeterminado"

    # Determinar o nome para pitch_control
    if pitch_control >= 0.9:
        pitch_name = "Avançando rápido"
    elif 0.1 <= pitch_control < 0.8:
        pitch_name = "Avançando"
    elif -0.1 < pitch_control < 0.1:
        pitch_name = "Parado"
    elif -0.8 <= pitch_control <= -0.1:
        pitch_name = "Recuando"
    elif pitch_control <= -0.9:
        pitch_name = "Recuando rápido"
    else:
        pitch_name = "Indeterminado"

    return yaw_name, pitch_name

# Inicializando Tkinter para a interface gráfica
# Cria a janela principal da interface gráfica com Tkinter.
root = tk.Tk()
root.title("Controle Diferencial da Cadeira de Rodas com Movimentos de Cabeça")
root.geometry("800x600")
root.configure(bg="#282828")

# Frame principal para posicionar a câmera e as setas
frame_main = tk.Frame(root, bg="#282828")
frame_main.pack(expand=True)

# Rótulo da câmera
camera_label = tk.Label(frame_main, bg="#282828", bd=2, relief="solid")

# Função para desenhar setas com Canvas
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
def create_arrow(canvas, direction, color, intensity=1):
    canvas.delete("all")
    color_intensity = int(255 * abs(intensity))
    # As setas serão vermelhas com intensidade variável
    color_hex = f'#{color_intensity:02x}{0:02x}{0:02x}'  # Tom de vermelho varia com a intensidade
    if direction == 'up':
        canvas.create_polygon([50, 10, 90, 90, 10, 90], fill=color_hex)
    elif direction == 'down':
        canvas.create_polygon([50, 90, 90, 10, 10, 10], fill=color_hex)
    elif direction == 'left':
        canvas.create_polygon([10, 50, 90, 10, 90, 90], fill=color_hex)
    elif direction == 'right':
        canvas.create_polygon([90, 50, 10, 10, 10, 90], fill=color_hex)

# Criação dos canvas para setas
canvas_up = tk.Canvas(frame_main, width=100, height=100, bg="#282828", highlightthickness=0)
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
create_arrow(canvas_up, 'up', 'white')

canvas_left = tk.Canvas(frame_main, width=100, height=100, bg="#282828", highlightthickness=0)
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
create_arrow(canvas_left, 'left', 'white')

canvas_right = tk.Canvas(frame_main, width=100, height=100, bg="#282828", highlightthickness=0)
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
create_arrow(canvas_right, 'right', 'white')

canvas_down = tk.Canvas(frame_main, width=100, height=100, bg="#282828", highlightthickness=0)
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
create_arrow(canvas_down, 'down', 'white')

# Posicionamento dos elementos usando grid
canvas_up.grid(row=0, column=1, pady=5)
canvas_left.grid(row=1, column=0, padx=5)
camera_label.grid(row=1, column=1)
canvas_right.grid(row=1, column=2, padx=5)
canvas_down.grid(row=2, column=1, pady=5)

# Texto de comando
command_label = tk.Label(root, text="Aguardando detecção...", font=("Helvetica", 16, "bold"), fg="#00FF00", bg="#000000")
command_label.pack(pady=10)

# Indicador de trava
lock_label = tk.Label(root, text="Estado: Bloqueado", font=("Helvetica", 14, "bold"), fg="#FF0000", bg="#000000")
lock_label.pack(pady=5)

# Barras de progresso para visualização dos controles
control_frame = tk.Frame(root, bg="#282828")
control_frame.pack(pady=10)

tk.Label(control_frame, text="Controle de Direção (Yaw):", fg="white", bg="#282828").grid(row=0, column=0, padx=5)
yaw_progress = ttk.Progressbar(control_frame, orient='horizontal', length=200, mode='determinate')
yaw_progress.grid(row=0, column=1, padx=5)

tk.Label(control_frame, text="Controle de Velocidade (Pitch):", fg="white", bg="#282828").grid(row=1, column=0, padx=5)
pitch_progress = ttk.Progressbar(control_frame, orient='horizontal', length=200, mode='determinate')
pitch_progress.grid(row=1, column=1, padx=5)

# Adiciona slider para sensibilidade do yaw
slider_frame = tk.Frame(root, bg="#282828")
slider_frame.pack(pady=10)

tk.Label(slider_frame, text="Sensibilidade Direita/Esquerda:", fg="white", bg="#282828").pack(side=tk.LEFT, padx=5)
yaw_sens_var = tk.DoubleVar(value=1.0)
yaw_slider = tk.Scale(slider_frame, from_=0.5, to=3.0, resolution=0.05, orient=tk.HORIZONTAL, variable=yaw_sens_var, length=200, bg="#282828", fg="white", highlightthickness=0)
yaw_slider.pack(side=tk.LEFT)

# Função para atualizar as setas com base nos valores de controle
def update_arrows_based_on_control(yaw_control, pitch_control):
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
    create_arrow(canvas_up, 'up', 'red', intensity=max(0, pitch_control))
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
    create_arrow(canvas_down, 'down', 'red', intensity=max(0, -pitch_control))
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
    create_arrow(canvas_left, 'left', 'red', intensity=max(0, -yaw_control))
# Função que desenha setas indicadoras na interface, variando a intensidade pela direção.
    create_arrow(canvas_right, 'right', 'red', intensity=max(0, yaw_control))

def update_camera_frame(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(frame_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    camera_label.imgtk = img_tk
    camera_label.config(image=img_tk)

def draw_landmarks_and_direction(frame, landmarks_points, yaw, pitch, EAR):
    for (x, y) in landmarks_points:
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # Pontos verdes

    left_eye = landmarks_points[36:42]
    right_eye = landmarks_points[42:48]
    nose = landmarks_points[30]
    cv2.polylines(frame, [np.array(left_eye, dtype=np.int32)], True, (255, 255, 0), 1)  # Olho esquerdo
    cv2.polylines(frame, [np.array(right_eye, dtype=np.int32)], True, (255, 255, 0), 1)  # Olho direito
    cv2.line(frame, ((left_eye[0][0] + right_eye[0][0]) // 2, (left_eye[0][1] + right_eye[0][1]) // 2), nose, (255, 0, 255), 2)  # Linha para o nariz

    # Desenhar contorno branco para o texto
    cv2.putText(frame, f"Yaw: {int(yaw)}°", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 4)
    cv2.putText(frame, f"Pitch: {int(pitch)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 4)

    # Desenhar texto preto por cima
    cv2.putText(frame, f"Yaw: {int(yaw)}°", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(frame, f"Pitch: {int(pitch)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Desenhar EAR na tela para depuração
    cv2.putText(frame, f"EAR: {EAR:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

# Função principal de detecção: identifica rosto, calcula yaw/pitch, detecta piscadas, controla comandos.
def detect_head_movements():
# Se detectar duas piscadas rápidas, desbloqueia a cadeira de rodas.
    global initial_nose_y, COUNTER, TOTAL_BLINKS, double_blink_detected
    global is_locked, last_blink_time, last_movement_time

    detector = dlib.get_frontal_face_detector()
    try:
# Carrega o modelo pré-treinado com 68 pontos de referência do rosto (landmarks).
        
            current_dir = os.path.dirname(os.path.abspath(__file__))
            predictor_path = os.path.join(current_dir, "shape_predictor_68_face_landmarks.dat")
            predictor = dlib.shape_predictor(predictor_path)

    except RuntimeError as e:
# Carrega o modelo pré-treinado com 68 pontos de referência do rosto (landmarks).
        print("Erro ao carregar o shape_predictor_68_face_landmarks.dat:", e)
        return

# Inicializa a câmera para capturar os movimentos do usuário em tempo real.
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao abrir a câmera.")
        return

    # Reduz a resolução para melhorar performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  # Resolução reduzida
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    # Ajuste com base na calibração
    max_yaw_angle = 30  # Ângulo máximo de yaw considerado (em graus)
    max_pitch_displacement = 20  # Deslocamento máximo de pitch (em pixels) - ajuste após calibração
    dead_zone_yaw_min = -10
    dead_zone_yaw_max = 10
    dead_zone_pitch_min = -10
    dead_zone_pitch_max = 10

    frame_count = 0  # Para processar 1 a cada N frames

    def process_frame():
        global is_locked, last_blink_time, last_movement_time, initial_nose_y, COUNTER, TOTAL_BLINKS, double_blink_detected
        nonlocal frame_count
        ret, frame = cap.read()
        if not ret:
            root.after(20, process_frame)
            return

        frame_count += 1
        # Processa apenas 1 a cada 2 frames para aliviar CPU
        if frame_count % 2 == 0:
            update_camera_frame(frame)
            root.after(20, process_frame)
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 1)

        if len(faces) > 0:
            for face in faces:
                landmarks = predictor(gray, face)
                landmarks_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(68)]

                left_eye = landmarks_points[36:42]
                right_eye = landmarks_points[42:48]
                EAR_left = calculate_EAR(left_eye)
                EAR_right = calculate_EAR(right_eye)
                EAR = (EAR_left + EAR_right) / 2.0

                # Verificação de piscada
                if EAR < EAR_THRESHOLD:
                    COUNTER += 1
                else:
                    if COUNTER >= CONSEC_FRAMES:
                        TOTAL_BLINKS += 1
                        current_time = time.time()
                        if TOTAL_BLINKS == 1:
                            last_blink_time = current_time
                        elif TOTAL_BLINKS == 2:
                            if (current_time - last_blink_time) <= DOUBLE_BLINK_TIME:
                                double_blink_detected = True
                                is_locked = False
                                lock_label.config(text="Estado: Desbloqueado", fg="#00FF00")
                                last_movement_time = time.time()
                            TOTAL_BLINKS = 0
                    COUNTER = 0

                if TOTAL_BLINKS > 0 and (time.time() - last_blink_time) > DOUBLE_BLINK_TIME:
                    TOTAL_BLINKS = 0

                yaw_current = calculate_yaw_using_eyes(landmarks_points)
                pitch_current = calculate_pitch_using_nose(landmarks_points)

                yaw_values.append(yaw_current)
                pitch_values.append(pitch_current)

                yaw_avg = np.mean(yaw_values)
                pitch_avg = np.mean(pitch_values)

                if dead_zone_yaw_min <= yaw_avg <= dead_zone_yaw_max and dead_zone_pitch_min <= pitch_avg <= dead_zone_pitch_max:
                    yaw_control = 0.0
                    pitch_control = 0.0
                else:
                    # Aplica o ganho do slider de sensibilidade
                    yaw_gain = yaw_sens_var.get()
                    yaw_control = np.clip((yaw_avg / max_yaw_angle) * yaw_gain, -1, 1)
                    pitch_control = np.clip(pitch_avg / max_pitch_displacement, -1, 1)

                movement_detected = (yaw_control != 0.1) or (pitch_control != 0.1)

                if movement_detected:
                    last_movement_time = time.time()

                if not is_locked and last_movement_time is not None:
                    if (time.time() - last_movement_time) > LOCK_TIMEOUT:
                        is_locked = True
                        lock_label.config(text="Estado: Bloqueado", fg="#FF0000")
                        send_coppelia_command(0, 0)

                if not is_locked:
                    if movement_detected:
                        max_speed = 3.5
                        left_wheel_speed = (pitch_control - yaw_control) * max_speed
                        right_wheel_speed = (pitch_control + yaw_control) * max_speed
                        send_coppelia_command(left_wheel_speed, right_wheel_speed)
                        yaw_name, pitch_name = get_direction_names(yaw_control, pitch_control)
                        action = f"{pitch_name}, {yaw_name}"
                        command_label.config(text=action)
                        update_arrows_based_on_control(yaw_control, pitch_control)
                        yaw_progress['value'] = (yaw_control + 1) * 50
                        pitch_progress['value'] = (pitch_control + 1) * 50
                        draw_landmarks_and_direction(frame, landmarks_points, yaw_avg, pitch_avg, EAR)
                    else:
                        send_coppelia_command(0, 0)
                        command_label.config(text="Parado")
                        update_arrows_based_on_control(0, 0)
                        yaw_progress['value'] = 50
                        pitch_progress['value'] = 50
                else:
                    send_coppelia_command(0, 0)
                    command_label.config(text="Trancado")
                    update_arrows_based_on_control(0, 0)
                    yaw_progress['value'] = 50
                    pitch_progress['value'] = 50

                draw_landmarks_and_direction(frame, landmarks_points, yaw_avg, pitch_avg, EAR)
        else:
            send_coppelia_command(0, 0)
            command_label.config(text="Nenhuma face detectada")
            update_arrows_based_on_control(0, 0)
            yaw_progress['value'] = 50
            pitch_progress['value'] = 50
            global initial_nose_y
            initial_nose_y = None
            pitch_values.clear()
            yaw_values.clear()
            if not is_locked:
                is_locked = True
                lock_label.config(text="Estado: Bloqueado", fg="#FF0000")
                send_coppelia_command(0, 0)

        update_camera_frame(frame)
        root.after(20, process_frame)  # ~50 FPS

    # Inicie o loop otimizado
    process_frame()
    # Não precisa mais de while True ou Thread
    # root.mainloop() já está fora desta função

detect_head_movements()  # Chama a função otimizada

# Inicializa a interface gráfica
root.mainloop()

# Fechar a conexão com o CoppeliaSim
# Encerra a conexão com o CoppeliaSim após o fechamento da aplicação.
sim.simxFinish(clientID)