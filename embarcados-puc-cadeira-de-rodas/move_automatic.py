import sys
import time
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Listener
from collections import deque
import numpy as np

# Configuração da API do CoppeliaSim (mesma estrutura anterior)
sys.path.append('caminho/para/coppelia_api')  # Ajuste o caminho
try:
    import sim
except Exception as e:
    print("Erro ao importar a API do CoppeliaSim:", e)
    sys.exit(1)

# Inicialização da conexão com CoppeliaSim (mesma função anterior)
def initialize_coppelia():
    sim.simxFinish(-1)
    clientID = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
    if clientID != -1:
        print("Conectado ao CoppeliaSim")
        return clientID
    else:
        print("Falha ao conectar ao CoppeliaSim")
        sys.exit(1)

clientID = initialize_coppelia()

# Variáveis globais para controle do mouse
mouse_x, mouse_y = 0, 0
last_mouse_x, last_mouse_y = 0, 0
movement_threshold = 50  # Sensibilidade do movimento (em pixels)

# Função para enviar comandos ao CoppeliaSim
def send_coppelia_command(left_wheel_speed, right_wheel_speed):
    try:
        command_str = f"{left_wheel_speed},{right_wheel_speed}"
        sim.simxSetStringSignal(clientID, 'wheelchair_command', command_str, sim.simx_opmode_oneshot)
        print(f"Comando enviado: {command_str}")
    except Exception as e:
        print(f"Erro ao enviar comando: {e}")

# Callback para movimento do mouse
def on_move(x, y):
    global mouse_x, mouse_y, last_mouse_x, last_mouse_y
    
    mouse_x, mouse_y = x, y
    dx = x - last_mouse_x
    dy = y - last_mouse_y
    
    # Resetar posição se o mouse sair da janela
    if abs(dx) > 500 or abs(dy) > 500:
        last_mouse_x, last_mouse_y = x, y
        return
    
    # Enviar comandos baseados no movimento
    if abs(dx) > movement_threshold or abs(dy) > movement_threshold:
        if abs(dx) > abs(dy):  # Movimento horizontal predominante
            if dx > 0:
                send_coppelia_command(2.0, -2.0)  # Direita
            else:
                send_coppelia_command(-2.0, 2.0)  # Esquerda
        else:  # Movimento vertical predominante
            if dy > 0:
                send_coppelia_command(2.0, 2.0)   # Frente
            else:
                send_coppelia_command(-2.0, -2.0) # Trás
        
        last_mouse_x, last_mouse_y = x, y

# Interface gráfica simplificada
root = tk.Tk()
root.title("Controle por Mouse")
root.geometry("400x200")

label = tk.Label(root, text="Mova o mouse para controlar a cadeira:\n- Para cima/baixo: Frente/Trás\n- Para os lados: Esquerda/Direita", font=("Arial", 12))
label.pack(pady=20)

# Iniciar listener do mouse
mouse_listener = Listener(on_move=on_move)
mouse_listener.start()

# Função para encerrar
def on_closing():
    mouse_listener.stop()
    sim.simxFinish(clientID)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()