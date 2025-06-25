import sys
import sim  # API do CoppeliaSim (deve estar no mesmo diretório)
import tkinter as tk
from tkinter import ttk

# Configuração da conexão com CoppeliaSim
def connect_coppelia():
    sim.simxFinish(-1)
    client_id = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
    if client_id == -1:
        print("Erro: Não foi possível conectar ao CoppeliaSim!")
        sys.exit(1)
    return client_id

client_id = connect_coppelia()

# Função para enviar comandos
def send_command(left_speed, right_speed):
    try:
        sim.simxSetStringSignal(client_id, 'wheelchair_command', 
                              f"{left_speed},{right_speed}", 
                              sim.simx_opmode_oneshot)
        print(f"Comando: Roda Esquerda={left_speed}, Roda Direita={right_speed}")
    except Exception as e:
        print("Erro ao enviar comando:", e)

# Funções de controle (chamadas pelos botões)
def move_forward():
    send_command(2.0, 2.0)  # Ambas as rodas para frente

def move_backward():
    send_command(-2.0, -2.0)  # Ambas as rodas para trás

def turn_left():
    send_command(-1.5, 1.5)   # Roda esquerda para trás, direita para frente

def turn_right():
    send_command(1.5, -1.5)   # Roda direita para trás, esquerda para frente

def stop():
    send_command(0, 0)        # Para as rodas

# Interface gráfica
root = tk.Tk()
root.title("Controle Manual da Cadeira")
root.geometry("300x200")

# Botões
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

btn_forward = tk.Button(btn_frame, text="↑", command=move_forward, width=5, height=2)
btn_forward.grid(row=0, column=1, padx=5, pady=5)

btn_left = tk.Button(btn_frame, text="←", command=turn_left, width=5, height=2)
btn_left.grid(row=1, column=0, padx=5, pady=5)

btn_stop = tk.Button(btn_frame, text="STOP", command=stop, width=5, height=2)
btn_stop.grid(row=1, column=1, padx=5, pady=5)

btn_right = tk.Button(btn_frame, text="→", command=turn_right, width=5, height=2)
btn_right.grid(row=1, column=2, padx=5, pady=5)

btn_backward = tk.Button(btn_frame, text="↓", command=move_backward, width=5, height=2)
btn_backward.grid(row=2, column=1, padx=5, pady=5)

# Label de status
status_label = tk.Label(root, text="Clique nos botões para controlar", fg="blue")
status_label.pack(pady=10)

# Encerramento
def on_close():
    stop()  # Para a cadeira ao fechar
    sim.simxFinish(client_id)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()