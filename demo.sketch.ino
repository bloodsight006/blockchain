void setup() {
  Serial.begin(9600); // Start serial communication
}

void loop() {
  // Simulate a temperature between 20 and 30 degrees
  int sensorValue = random(20, 30);
  
  // Send ONLY the number. This makes it easy for Python to read.
  Serial.println(sensorValue);
  
  delay(3000); // Send data every 3 seconds
}

