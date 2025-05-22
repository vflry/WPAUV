#include <Wire.h>
#include <MPU6050.h>
#include <SD.h>
#include <SPI.h>

MPU6050 mpu;
const int chipSelect = 10;

File dataFile;

unsigned long lastLogTime = 0;
const int logInterval = 50; // intervalle de 50 ms (20 Hz)

void setup() {
  Serial.begin(9600);
  Wire.begin();

  // Initialiser MPU6050
  Serial.println("Initialisation du MPU6050...");
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Erreur : MPU6050 non connecté !");
    while (1);
  }

  // Initialisation carte SD
  Serial.println("Initialisation de la carte SD...");
  if (!SD.begin(chipSelect)) {
    Serial.println("Erreur : carte SD non détectée !");
    while (1);
  }

  dataFile = SD.open("mpu_logs.csv", FILE_WRITE);
  if (dataFile) {
    dataFile.println("time_ms,ax,ay,az,gx,gy,gz"); // en-tête CSV
    dataFile.close();
    Serial.println("Fichier de log créé.");
  } else {
    Serial.println("Erreur : impossible de créer le fichier.");
    while (1);
  }
}

void loop() {
  if (millis() - lastLogTime >= logInterval) {
    lastLogTime = millis();

    int16_t ax, ay, az;
    int16_t gx, gy, gz;

    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Conversion brute vers unités SI :
    float accelScale = 16384.0;     // pour ±2g
    float gyroScale = 131.0;        // pour ±250°/s

    float fax = ax / accelScale * 9.81;
    float fay = ay / accelScale * 9.81;
    float faz = az / accelScale * 9.81;

    float fgx = gx / gyroScale;
    float fgy = gy / gyroScale;
    float fgz = gz / gyroScale;

    // Écriture sur carte SD
    dataFile = SD.open("mpu_logs.csv", FILE_WRITE);
    if (dataFile) {
      dataFile.print(millis());
      dataFile.print(",");
      dataFile.print(fax, 3);
      dataFile.print(",");
      dataFile.print(fay, 3);
      dataFile.print(",");
      dataFile.print(faz, 3);
      dataFile.print(",");
      dataFile.print(fgx, 3);
      dataFile.print(",");
      dataFile.print(fgy, 3);
      dataFile.print(",");
      dataFile.println(fgz, 3);
      dataFile.close();
    } else {
      Serial.println("Erreur écriture SD !");
    }

    // Affichage Serial (optionnel)
    Serial.print("A: ");
    Serial.print(fax, 2); Serial.print(", ");
    Serial.print(fay, 2); Serial.print(", ");
    Serial.print(faz, 2); Serial.print(" | G: ");
    Serial.print(fgx, 2); Serial.print(", ");
    Serial.print(fgy, 2); Serial.print(", ");
    Serial.println(fgz, 2);
  }
}
