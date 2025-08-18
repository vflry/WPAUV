#include <Wire.h>
#include <VL53L1X.h>
#include <SPI.h>
#include <SD.h>

VL53L1X sensor;
const int chipSelect = 53;
File logFile;

const int PIN_A0_ADC = A0;
const int PIN_A1_ADC = A1;
const int PIN_A2_ADC = A2;     // DC output from full bridge
const bool USE_EXTERNAL_AREF = false;
const float VREF = 5.000;

const uint32_t ANALOG_PERIOD_US = 1000; // 1 kHz sampling rate
const uint16_t FLUSH_EVERY_N_LINES = 100;
uint16_t lines_since_flush = 0;

volatile int lastDistance = -1;
unsigned long lastDistanceMs = 0;

inline float countsToVolt(int counts) {
  return counts * (VREF / 1023.0f);
}

// Set ADC prescaler to 32 for faster conversion (less precise but faster)
void setFastADC() {
  ADCSRA = (ADCSRA & ~((1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0))) | (1<<ADPS2) | (1<<ADPS0);
}

void printFloat(File& f, float val, int precision = 3) {
  char buf[16];
  dtostrf(val, 1, precision, buf);
  f.print(buf);
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (USE_EXTERNAL_AREF) {
    analogReference(EXTERNAL);
  } else {
    analogReference(DEFAULT);
  }

  setFastADC();

  pinMode(53, OUTPUT);
  digitalWrite(53, HIGH);

  Serial.println(F("Initializing sensor..."));
  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println(F("Sensor not detected!"));
    while (1);
  }
  sensor.setDistanceMode(VL53L1X::Short);
  sensor.setMeasurementTimingBudget(20000);
  sensor.startContinuous(1);

  Serial.println(F("Initializing SD card..."));
  if (!SD.begin(chipSelect)) {
    Serial.println(F("SD card error!"));
    while (1);
  }

  logFile = SD.open("mesures.csv", FILE_WRITE);
  if (!logFile) {
    Serial.println(F("File open error!"));
    while (1);
  }

  logFile.println(F("Time_ms,Distance_mm,VA0_V,VA1_V,VA2_V"));
  logFile.flush();
  Serial.println(F("Logging started!"));
}

void loop() {
  static uint32_t t0 = millis();
  static uint32_t nextAnalogTick = micros();

  // Read VL53 only when new measurement is ready
  if (sensor.dataReady()) {
    int d = sensor.read();
    if (!sensor.timeoutOccurred()) {
      lastDistance = d;
      lastDistanceMs = millis() - t0;
    }
  }

  // Timed analog sampling
  uint32_t now = micros();
  if ((int32_t)(now - nextAnalogTick) >= 0) {
    nextAnalogTick += ANALOG_PERIOD_US;

    int c0 = analogRead(PIN_A0_ADC);
    int c1 = analogRead(PIN_A1_ADC);
    int c2 = analogRead(PIN_A2_ADC);

    float vA0 = countsToVolt(c0);
    float vA1 = countsToVolt(c1);
    float vA2 = countsToVolt(c2);

    uint32_t t_ms = millis() - t0;

    // CSV output
    logFile.print(t_ms); logFile.print(',');
    logFile.print(lastDistance); logFile.print(',');
    printFloat(logFile, vA0, 3); logFile.print(',');
    printFloat(logFile, vA1, 3); logFile.print(',');
    printFloat(logFile, vA2, 3); logFile.println();

    if (++lines_since_flush >= FLUSH_EVERY_N_LINES) {
      logFile.flush();
      lines_since_flush = 0;
    }
  }
}
