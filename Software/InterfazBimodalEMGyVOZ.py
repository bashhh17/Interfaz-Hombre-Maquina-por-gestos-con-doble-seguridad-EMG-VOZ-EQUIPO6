import tkinter as tk
import sounddevice as sd
import numpy as np
import serial
import time
from collections import deque

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
PUERTO_SERIAL = 'COM3'
BAUD_RATE = 115200

# Umbrales
UMBRAL_EMG_ABRIR   = 12.0  
UMBRAL_EMG_CERRAR  = 22.0 


# --- 2. RÚBRICA: VENTANAS DESLIZANTES DE 2 SEGUNDOS ---
FS_VOZ = 16000
FS_EMG = 1000

# Buffers de 2 segundos exactos
buffer_voz = deque(np.zeros(int(FS_VOZ * 2.0)), maxlen=int(FS_VOZ * 2.0)) 
buffer_emg = deque(maxlen=int(FS_EMG * 2.0)) 

CHUNK_SIZE = int(FS_VOZ * 0.2) 
sistema_desbloqueado = False   # Memoria de estado (Flip-Flop)

# --- 3. CONEXIÓN SERIAL ---
print(f"Conectando a {PUERTO_SERIAL}...")
try:
    arduino = serial.Serial(PUERTO_SERIAL, BAUD_RATE, timeout=0)
    time.sleep(2) 
    arduino.reset_input_buffer()
except serial.SerialException:
    print(f"[ERROR] No se pudo conectar al puerto {PUERTO_SERIAL}.")
    exit()

# --- 4. EXTRACCIÓN Y PROCESAMIENTO DE SEÑALES ---
def callback_audio(indata, frames, time_info, status):
    buffer_voz.extend(indata[:, 0])

def clasificar_comando_baritono(energia, zcr):
    if energia < 700:
        return "Silencio"
    
    # "Cierra": Alta fricción (sibilancia de la C)
    if 3000  >  energia > 1000 and 0.15 < zcr < 0.25:
        return "Cierra"
        
    # "Abre": Vocal grave/abierta + Energía superando el umbral
    elif 6000  >  energia > 3000 and 0.09 < zcr < 0.13:
        return "Abre"
        
    return "Indefinido"

def analizar_voz():
    ventana = np.array(buffer_voz)
    
    energia = np.sum(ventana**2) * 1000.0 
    signos = np.sign(ventana)
    zcr = np.sum(np.abs(np.diff(signos))) / (2 * len(ventana))
    
    comando_voz = clasificar_comando_baritono(energia, zcr)
    return comando_voz, energia, zcr

def analizar_emg():
    while arduino.in_waiting > 0:
        try:
            linea = arduino.readline().decode('ascii').strip()
            if linea:
                buffer_emg.append(int(linea))
        except ValueError:
            pass 

    rms = 0.0
    
    if len(buffer_emg) > 500:
        ventana = np.array(buffer_emg)
        senal_ac = ventana - np.mean(ventana)
        rms = np.sqrt(np.mean(senal_ac**2))
            
    # Solo retornamos el número crudo, la lógica se hace en la interfaz
    return rms

# --- 5. LÓGICA CENTRAL Y GUI ---
def actualizar_gui():
    global sistema_desbloqueado
    
    comando_voz, energia, zcr = analizar_voz()
    rms = analizar_emg()
    
    # Evaluamos los dos niveles de fuerza
    emg_nivel_abrir = rms >= UMBRAL_EMG_ABRIR
    emg_nivel_cerrar = rms >= UMBRAL_EMG_CERRAR
    
    # Máquina de estados Bimodal
    if not sistema_desbloqueado:
        # ESTADO 1: BLOQUEADO (Buscamos "Abre" + Fuerza Alta)
        if comando_voz == "Abre" and emg_nivel_abrir:
            sistema_desbloqueado = True
            texto_estado = "DESBLOQUEADO"
            color_fondo = "#2ecc71" # Verde
            
        elif comando_voz == "Abre" or emg_nivel_abrir:
            texto_estado = "FALTA UNA SEÑAL (PARA ABRIR)"
            color_fondo = "#f39c12" # Naranja
            
        else:
            texto_estado = "BLOQUEADO"
            color_fondo = "#e74c3c" # Rojo
            
    else:
        # ESTADO 2: DESBLOQUEADO (Buscamos "Cierra" + Fuerza Baja)
        if comando_voz == "Cierra" and emg_nivel_cerrar:
            sistema_desbloqueado = False
            texto_estado = "BLOQUEADO"
            color_fondo = "#e74c3c" # Rojo
            
        elif comando_voz == "Cierra" or emg_nivel_cerrar:
            texto_estado = "FALTA UNA SEÑAL (PARA CERRAR)"
            color_fondo = "#f39c12" # Naranja
            
        else:
            texto_estado = "DESBLOQUEADO"
            color_fondo = "#2ecc71" # Verde

    # Refrescar textos visuales
    lbl_actuador.config(text=texto_estado, bg=color_fondo)
    
    color_voz = "#2ecc71" if comando_voz == "Abre" else "#e74c3c" if comando_voz == "Cierra" else "#3498db"
    lbl_voz.config(text=f"Voz: {comando_voz} (E: {energia:.1f} | ZCR: {zcr:.3f})", fg=color_voz)
    
    # Modificamos la etiqueta del EMG para que te indique qué umbral está vigilando
    if sistema_desbloqueado:
        lbl_emg.config(text=f"EMG Activo (> {UMBRAL_EMG_CERRAR}): {'SÍ' if emg_nivel_cerrar else 'NO'} (RMS: {rms:.1f})")
    else:
        lbl_emg.config(text=f"EMG Activo (> {UMBRAL_EMG_ABRIR}): {'SÍ' if emg_nivel_abrir else 'NO'} (RMS: {rms:.1f})")
    
    ventana.after(200, actualizar_gui)

# --- 6. INTERFAZ GRÁFICA ---
ventana = tk.Tk()
ventana.title("Interfaz Bimodal - Máquina de Estados Continua")
ventana.geometry("600x320")
ventana.configure(bg="#2c3e50")

tk.Label(ventana, text="Control Bimodal (Ventana 2s)", font=("Arial", 16, "bold"), fg="white", bg="#2c3e50").pack(pady=15)

lbl_voz = tk.Label(ventana, text="Voz...", font=("Consolas", 14), fg="#3498db", bg="#2c3e50")
lbl_voz.pack(pady=5)

lbl_emg = tk.Label(ventana, text="EMG...", font=("Consolas", 14), fg="#9b59b6", bg="#2c3e50")
lbl_emg.pack(pady=5)

lbl_actuador = tk.Label(ventana, text="INICIANDO...", font=("Arial", 22, "bold"), width=30, height=3, bg="gray", fg="white", relief="raised")
lbl_actuador.pack(pady=25)

flujo_audio = sd.InputStream(samplerate=FS_VOZ, channels=1, blocksize=CHUNK_SIZE, callback=callback_audio)
flujo_audio.start()

ventana.after(200, actualizar_gui)
ventana.mainloop()

flujo_audio.stop()
if arduino.is_open:
    arduino.close()