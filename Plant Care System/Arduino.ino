// ==========================================
// 1. PIN DEFINITIONS
// ==========================================

// --- ENVIRONMENTAL SENSORS ---
const int MOISTURE_PIN = A0;      // Moisture Sensor
const int LIGHT_PIN = A1;         // Light Sensor

// --- ACTUATORS (RELAYS) ---
const int PUMP_PIN = 12;          // Pump Relay
const int LAMP_PIN = 13;          // Lamp Relay

// --- MOTORS (L298N) ---
const int ENA = 7;    
const int IN1 = 6;
const int IN2 = 5;
const int IN3 = 4;
const int IN4 = 3;
const int ENB = 2;    

// --- DISTANCE SENSORS (ULTRASONIC) ---
const int TRIG_FRONT = 10;
const int ECHO_FRONT = 11;
const int TRIG_BACK = 8;
const int ECHO_BACK = 9;

// ==========================================
// 2. CALIBRATION THRESHOLDS
// ==========================================

const int DRY_THRESHOLD = 800;    // Dry if >= 800
const int LIGHT_THRESHOLD = 200;  // Dark if < 200
const int OBSTACLE_DIST = 15;     // 15 cm danger distance

// --- SYSTEM VARIABLES ---
bool isLampOn = false;            

// ==========================================
// 3. SETUP FUNCTION
// ==========================================

void setup() {
  // Initialize Pins
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(LAMP_PIN, OUTPUT);
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(TRIG_FRONT, OUTPUT); pinMode(ECHO_FRONT, INPUT);
  pinMode(TRIG_BACK, OUTPUT); pinMode(ECHO_BACK, INPUT);

  // Stop all components initially
  digitalWrite(PUMP_PIN, HIGH); 
  digitalWrite(LAMP_PIN, HIGH); 
  stopMotors();

  Serial.begin(9600);
  Serial.println("System Initialized. Starting after 5 seconds...");
  
  // Initial wait command (5 seconds)
  delay(5000); 
  Serial.println("Initial wait finished. System operational.");
}

// ==========================================
// 4. MAIN LOOP FUNCTION
// ==========================================

void loop() {
  
  // ---------------------------------------------------------
  // DIAGNOSTICS & SENSOR READING (EVERY CYCLE)
  // ---------------------------------------------------------
  int moisture = analogRead(MOISTURE_PIN);
  
  // Print moisture reading for diagnostics
  Serial.print("RAW MOISTURE (A0): "); 
  Serial.print(moisture);
  Serial.print(" | Status: ");
  
  // ---------------------------------------------------------
  // PHASE 1: MOISTURE CHECK & PUMP CONTROL
  // ---------------------------------------------------------
  if (moisture >= DRY_THRESHOLD) {
    // Soil is dry
    Serial.println("DRY (>800). PUMP ON for 5s...");
    
    // Run pump for 5 seconds
    digitalWrite(PUMP_PIN, LOW);  
    delay(5000);                  
    digitalWrite(PUMP_PIN, HIGH); 
    
    // Wait 2 seconds before checking again (creates a 5s ON / 2s OFF cycle)
    Serial.println("   [PUMP] OFF. Waiting 2s before next check.");
    delay(2000); 
    
  } else {
    // Soil is wet
    digitalWrite(PUMP_PIN, HIGH); // Ensure pump is stopped
    Serial.println("WET (<800). PUMP OFF. Waiting 2s.");
    
    // 2-second delay to prevent CPU hogging
    delay(2000); 
  }

  // ---------------------------------------------------------
  // PHASE 2: LIGHT & MOVEMENT LOGIC
  // ---------------------------------------------------------
  
  int light = analogRead(LIGHT_PIN);
  
  // Case A: Area is dark + Lamp is OFF
  if (light < LIGHT_THRESHOLD && !isLampOn) {
    // Pass reading to the function strictly for diagnostics
    searchForLight(light); 
  }
  
  // Case B: Lamp is ON + Natural light detected
  else if (light >= LIGHT_THRESHOLD && isLampOn) {
    Serial.println("-> NATURAL LIGHT: Turning Lamp OFF.");
    digitalWrite(LAMP_PIN, HIGH); 
    isLampOn = false;
  }
}

// ==========================================
// 5. HELPER FUNCTIONS
// ==========================================

// --- LIGHT SEARCH FUNCTION ---
void searchForLight(int initialLight) {
  
  unsigned long moveStartTime = millis(); 
  bool lightFound = false;
  bool obstacleHit = false;

  Serial.println("-> DARKNESS DETECTED: Starting search sequence.");
  moveForward();
  // ... (Rest of movement and reverse logic follows previous logic) ...
  
  while (millis() - moveStartTime < 5000) {
    
    int dist = getDistance(TRIG_FRONT, ECHO_FRONT);
    if (dist <= OBSTACLE_DIST) {
      obstacleHit = true;
      break; 
    }

    int lightNow = analogRead(LIGHT_PIN);
    if (lightNow >= LIGHT_THRESHOLD) {
      lightFound = true;
      break; 
    }
    
    delay(50); 
  }

  stopMotors();

  if (lightFound) {
    Serial.println("   [SEARCH] Natural Light Found! Stopping.");
    return; 
  }
  else if (obstacleHit) {
    Serial.println("   [ACTION] Obstacle Avoidance: Reversing for 2 seconds...");
    moveBackward();
    delay(2000); 
    stopMotors();
    turnLampOn();
  }
  else {
    Serial.println("   [ACTION] Time limit reached (5s). Reversing for 5 seconds (Base)...");
    moveBackward();
    delay(5000); 
    stopMotors();
    turnLampOn();
  }
}

// --- LAMP CONTROL ---
void turnLampOn() {
    Serial.println("   [LAMP] Turning Lamp ON.");
    digitalWrite(LAMP_PIN, LOW); // Turn ON
    isLampOn = true;
}

// --- MOVEMENT FUNCTIONS ---
void moveForward() {
  digitalWrite(ENA, HIGH); digitalWrite(ENB, HIGH);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}

void moveBackward() {
  digitalWrite(ENA, HIGH); digitalWrite(ENB, HIGH);
  digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);
}

void stopMotors() {
  digitalWrite(ENA, LOW); digitalWrite(ENB, LOW);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

// --- DISTANCE MEASUREMENT ---
int getDistance(int trig, int echo) {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long duration = pulseIn(echo, HIGH, 25000); 
  if (duration == 0) return 999; 
  return duration * 0.034 / 2;
}