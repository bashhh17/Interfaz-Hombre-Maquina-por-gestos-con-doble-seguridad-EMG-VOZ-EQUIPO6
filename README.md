# Sistema HMI Bimodal EMG + Voz

Interfaz hombre-máquina bimodal que combina señales de EMG y voz para 
controlar un sistema de bloqueo/desbloqueo. Desarrollado como proyecto 
final de la materia de Análisis de Señales y Sistemas Biomédicos.

## Descripción

El sistema interpreta simultáneamente:
- **EMG:** dos umbrales de RMS para detectar apertura y cierre de mano
- **Voz:** umbrales de ZCR y Energía para reconocer las palabras "Abre" y "Cierra"

Ambas señales se procesan en una ventana temporal de 200 ms. 
El sistema permanece bloqueado si alguna de las dos señales está ausente.

---

## Requisitos de Hardware

- Arduino UNO
- Electrodos de superficie (x3) para EMG
- Micrófono
- Circuito de acondicionamiento de señal (AD620 + TL081/LM358)
- Fuente de alimentación ±5V

## Requisitos de Software

- Python 3.x
- Librerías necesarias:

pip install pyserial numpy pyqt6

---

## Pasos para ejecutar el proyecto

### 1. Conectar el hardware

1. Armar el circuito de acondicionamiento según el esquemático en `/Hardware`
2. Colocar los electrodos en el antebrazo (canal diferencial sobre el músculo flexor)
3. Conectar el Arduino UNO por USB
4. Verificar el puerto COM asignado

### 2. Cargar el código en Arduino

1. Abrir el archivo `/Software/LecturaDeDatosArduinoUNO.ino` en el IDE de Arduino
2. Seleccionar la placa **Arduino UNO** y el puerto correcto
3. Cargar el sketch

### 3. Ejecutar la interfaz en Python

1. Abrir el archivo `/Software/InterfazBimodalEMGyVOZ.py` en VisualStudio Code
3. Ejecute el programa

### 5. Calibración

2. Realizar apertura y cierre de mano para establecer umbrales
3. Pronunciar "Abre" y "Cierra" para calibrar los umbrales de voz en las lineas de código correspondiente


## Integrantes

- Jessica Cordoba Valdivia
- Sebastian Arguelles Chimal

**Universidad Veracruzana — Facultad de Instrumentación Electrónica**
