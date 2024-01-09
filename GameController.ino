#define RIGHT_BUTTON 6
#define LEFT_BUTTON 19

#define RIGHT_VRX A0
#define RIGHT_VRY A1
#define LEFT_VRX A2
#define LEFT_VRY A3

#define LEFT_JS_BUTTON A4
#define RIGHT_JS_BUTTON 4


#define RED 3
#define GREEN 9
#define BLUE 10

#define NUM_SENSORS 8

int lastVals[NUM_SENSORS] = { 0 };

bool isConnected = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(LEFT_BUTTON, INPUT_PULLUP);
  pinMode(RIGHT_BUTTON, INPUT_PULLUP);
  pinMode(LEFT_JS_BUTTON, INPUT_PULLUP);
  pinMode(RIGHT_JS_BUTTON, INPUT_PULLUP);

  pinMode(RIGHT_VRX, INPUT);
  pinMode(LEFT_VRX, INPUT);

  pinMode(RIGHT_VRY, INPUT);
  pinMode(LEFT_VRY, INPUT);

  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);

  Serial.begin(1000000);

  connect();
}

void connect() {
  if (isConnected) {
    return;
  }

  int count = 0;
  int colorVal = 10;
  bool forward = true;
  String s;
  do {
    while (!Serial.available()) {
    if (count % 50 == 0) if (forward) colorVal++; else colorVal--;
    if (forward) count++; else count--;
    if (count == 2000 || count == 0) forward = !forward;
    setLED(colorVal * 4, colorVal / 4, 0);
    delayMicroseconds(300);
    }
    s = Serial.readStringUntil('\n');
    

  } while (!s.equals("ready"));

  Serial.println("OK");

  while (Serial.available()) {
    Serial.read();
  }
  

  analogWrite(RED, 0);
  analogWrite(GREEN, 0);
  isConnected = true;
}

void setLED(byte red, byte green, byte blue) {
  if (red > 100) red = 100;
  if (green > 100) green = 100;
  if (blue > 100) blue = 100;
  analogWrite(RED, red);
  analogWrite(GREEN, green);
  analogWrite(BLUE, blue);
}

void checkForCommand() {
  if (Serial.available()) {
    String s = Serial.readStringUntil('\n');
    if (s == "LED") {
      while (!Serial.available()) continue;
      byte colors[3];
      Serial.readBytes(colors, 3);
      setLED(colors[0], colors[1], colors[2]);
    }
  }
}


void printState(int* values, int size) {
  checkForCommand();
  for (int i = 0; i < size; i++) {
    if (i < 2 || i == 4 || i == 5)
      Serial.println(values[i] >> 2);
    else
      Serial.println(values[i]);
  }

  Serial.println();
}


void outState(int* values, int size) {
  checkForCommand();
  Serial.write((byte) (values[0] >> 2)); // LEFT VRX
  Serial.write((byte) (values[1] >> 2)); // LEFT VRY
  Serial.write((byte) (values[4] >> 2)); // RIGHT VRX
  Serial.write((byte) (values[5] >> 2)); // RIGHT VRY

  //                       LEFT_BUTTON   LEFT_JS_BUTTON      RIGHT_BUTTON       RIGHT_JS_BUTTON
  byte combined_digitals = (values[2]) + (values[3] << 1) + (values[6] << 2) + (values[7] << 3);
  Serial.write(combined_digitals);
}


void loop() {
  int currentVals[] = { analogRead(LEFT_VRX), analogRead(LEFT_VRY), !digitalRead(LEFT_BUTTON), !digitalRead(LEFT_JS_BUTTON), 
                          analogRead(RIGHT_VRX), analogRead(RIGHT_VRY), !digitalRead(RIGHT_BUTTON), !digitalRead(RIGHT_JS_BUTTON) };

  for (int i = 0; i < NUM_SENSORS; i++) {
    if (currentVals[i] != lastVals[i]) {
      delay(1);
      outState(currentVals, NUM_SENSORS);
      break;
    }
  }

  for (int i = 0; i < NUM_SENSORS; i++) lastVals[i] = currentVals[i];

}
