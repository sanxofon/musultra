/*
* Ultrasonic Sensor HC-SR04 and Arduino Tutorial
*/
// defines pins numbers
const int trigPin = 9;
const int echoPin = 10;
const int redPin = 6;
const int grePin = 5;
const int bluPin = 3;
// defines variables
long duration;
int distance;
int prendido=0;
int maxset=1000;

void setup() {
  
    pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
    pinMode(echoPin, INPUT); // Sets the echoPin as an Input
    pinMode(redPin, OUTPUT); // Sets the ledPin as an Output
    pinMode(grePin, OUTPUT); // Sets the ledPin as an Output
    pinMode(bluPin, OUTPUT); // Sets the ledPin as an Output
    Serial.begin(9600); // Starts the serial communication
    
}
void loop() {
    if (Serial.available()) {
        int state = Serial.parseInt();
        if (state == 1) {
            prendido = 1;
            setColor(255, 0, 0);
            // digitalWrite(ledPin, HIGH);
        }
        if (state == 2) {
            prendido = 0;
            setColor(0, 0, 0);
            // digitalWrite(ledPin, LOW);
        }
    } else {
        // Clears the trigPin
        digitalWrite(trigPin, LOW);
        delayMicroseconds(2);
        
        // Sets the trigPin on HIGH state for 10 micro seconds
        digitalWrite(trigPin, HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin, LOW);
        
        // Reads the echoPin, returns the sound wave travel time in microseconds
        duration = pulseIn(echoPin, HIGH);
        
        // Calculating the distance
        // distance= duration*0.034/2; //cm
        distance= duration*0.34/2; //mm
        if (prendido==1 && distance<maxset) {
          if (distance<50) {
              setRGB(50,maxset,maxset);
          } else {
              setRGB(50,maxset,maxset-distance);
          }
          // setColor(distance, 255-distance, 0);
        }
        // Prints the distance on the Serial Monitor
        // Serial.print("Distance: ");
        if (distance<800) {
            Serial.println(distance);
        }
    }
}

void setRGB(float minimum, float maximum, int value) {
    float ratio = 2 * (value-minimum) / (maximum - minimum);
    int b = 255*(1 - ratio);
    if (b<0) {
      b=0;
    }
    int r = 255*(ratio - 1);
    if (r<0) {
      r=0;
    }
    int g = 255 - b - r;
    setColor(r,g,b);
    // return r, g, b
}
void setColor(int red, int green, int blue)
{
  #ifdef COMMON_ANODE
    red = 255 - red;
    green = 255 - green;
    blue = 255 - blue;
  #endif
  analogWrite(redPin, red);
  analogWrite(grePin, green);
  analogWrite(bluPin, blue);  
}
