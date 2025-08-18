#include <Wire.h>
#include <MPU6050.h>
#include <SD.h>
#include <SPI.h>

MPU6050 mpu;
const int chipSelect = 10;

File dataFile;

unsigned long lastLogTime = 0;
const int logInterval = 50;

void setup() {
  Serial.begin(9600);
  Wire.begin();

  Serial.println("Initializing MPU6050...");
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Error: MPU6050 not connected!");
    while (1);
  }

  Serial.println("Initializing SD card...");
  if (!SD.begin(chipSelect)) {
    Serial.println("Error: SD card not detected!");
    while (1);
  }

  dataFile = SD.open("mpu_logs.csv", FILE_WRITE);
  if (dataFile) {
    dataFile.println("time_ms,ax,ay,az,gx,gy,gz");
    dataFile.close();
    Serial.println("Log file created.");
  } else {
    Serial.println("Error: cannot create file.");
    while (1);
  }
}

void loop() {
  delay(25);
  if (millis() - lastLogTime >= logInterval) {
    lastLogTime = millis();

    int16_t ax, ay, az;
    int16_t gx, gy, gz;

    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Convert to standard units
    float accelScale = 16384.0;     // ±2g range
    float gyroScale = 131.0;        // ±250°/s range

    float fax = ax / accelScale * 9.81;
    float fay = ay / accelScale * 9.81;
    float faz = az / accelScale * 9.81;

    float fgx = gx / gyroScale;
    float fgy = gy / gyroScale;
    float fgz = gz / gyroScale;

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
      Serial.println("Error writing to SD!");
    }
  }

}
