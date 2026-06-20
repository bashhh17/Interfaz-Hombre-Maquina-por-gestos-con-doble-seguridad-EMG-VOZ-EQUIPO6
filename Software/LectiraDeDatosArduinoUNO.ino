const int pinEMG = A0; // Pin analógico donde está conectado tu sensor muscular

void setup() {
  // Velocidad de comunicación crítica (debe coincidir con BAUD_RATE = 115200 en Python)
  Serial.begin(115200);
  
  // Pequeña pausa de seguridad para estabilizar el microcontrolador al encender
  delay(1000); 
}

void loop() {
  // 1. Capturar el voltaje crudo del músculo (valores de 0 a 1023)
  int valorEMG = analogRead(pinEMG);
  
  // 2. Imprimir con salto de línea (println). 
  Serial.println(valorEMG); 
  
  // 3. Retardo de 1 milisegundo. 
  // Esto nos da una Frecuencia de Muestreo (FS) aproximada de 1000 Hz, 
  delay(1); 
}