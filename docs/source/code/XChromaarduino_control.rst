XChroma.arduino\_control module
===============================


.. autosummary::
   :nosignatures:

   XChroma.arduino_control.ArduinoController


.. automodule:: XChroma.arduino_control
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: groupwise



=======

Arduino Code Documentation
--------------------------

How to Use
**********

Send serial commands to control the servos:

.. list-table:: Servo Control Commands
   :widths: 10 30
   :header-rows: 1

   * - Command
     - Action
   * - **'a'**
     - Open Servo 1
   * - **'A'**
     - Close Servo 1
   * - **'z'**
     - Open Servo 2
   * - **'Z'**
     - Close Servo 2
   * - **'e'**
     - Open Servo 3
   * - **'E'**
     - Close Servo 3
   * - **'r'**
     - Reset (all closed)
   * - **'R'**
     - Reset (all open)

Example Serial Input:

.. code-block:: none

   a  → Servo 1 opens
   A  → Servo 1 closes
   R  → All servos open


---------


Arduino Code
************

Code used to control servos via serial commands.

.. tab-set::

    .. tab-item:: Full Code

        .. code-block:: cpp
            :linenos:

            #include <Servo.h>

            // Create Servo objects
            Servo servo1;
            Servo servo2;
            Servo servo3;

            // Servo pins
            const int pinServo1 = 9;
            const int pinServo2 = 10;
            const int pinServo3 = 11;

            // Servo positions
            const int positionOuverte1 = 0;
            const int positionOuverte2 = 0;
            const int positionOuverte3 = 90;
            const int positionFermee1 = 90;
            const int positionFermee2 = 90;
            const int positionFermee3 = 0;

            void setup() {
                servo1.attach(pinServo1);
                servo2.attach(pinServo2);
                servo3.attach(pinServo3);
                servo1.write(positionFermee1);
                servo2.write(positionFermee2);
                servo3.write(positionFermee3);
                Serial.begin(9600);
            }

            void loop() {
                if (Serial.available()) {
                char command = Serial.read();

                switch (command) {
                    case 'a': servo1.write(positionOuverte1); Serial.println("Servo 1: Open"); break;
                    case 'A': servo1.write(positionFermee1); Serial.println("Servo 1: Closed"); break;
                    case 'z': servo2.write(positionOuverte2); Serial.println("Servo 2: Open"); break;
                    case 'Z': servo2.write(positionFermee2); Serial.println("Servo 2: Closed"); break;
                    case 'e': servo3.write(positionOuverte3); Serial.println("Servo 3: Open"); break;
                    case 'E': servo3.write(positionFermee3); Serial.println("Servo 3: Closed"); break;
                    case 'r':
                    servo1.write(positionFermee1);
                    servo2.write(positionFermee2);
                    servo3.write(positionFermee3);
                    Serial.println("All servos are in the closed position.");
                    break;
                    case 'R':
                    servo1.write(positionOuverte1);
                    servo2.write(positionOuverte2);
                    servo3.write(positionOuverte3);
                    Serial.println("All servos are in the open position.");
                    break;
                    default: Serial.println("Unknown command. Use a/A, z/Z, e/E, or r."); break;
                }
                }
                delay(100);
            }

    .. tab-item:: Setup & Loop Only

        .. code-block:: cpp
            :linenos:

            void setup() {
                servo1.attach(pinServo1);
                servo2.attach(pinServo2);
                servo3.attach(pinServo3);
                servo1.write(positionFermee1);
                servo2.write(positionFermee2);
                servo3.write(positionFermee3);
                Serial.begin(9600);
            }

            void loop() {
                if (Serial.available()) {
                char command = Serial.read();

                switch (command) {
                    case 'a': servo1.write(positionOuverte1); Serial.println("Servo 1: Open"); break;
                    case 'A': servo1.write(positionFermee1); Serial.println("Servo 1: Closed"); break;
                    case 'z': servo2.write(positionOuverte2); Serial.println("Servo 2: Open"); break;
                    case 'Z': servo2.write(positionFermee2); Serial.println("Servo 2: Closed"); break;
                    case 'e': servo3.write(positionOuverte3); Serial.println("Servo 3: Open"); break;
                    case 'E': servo3.write(positionFermee3); Serial.println("Servo 3: Closed"); break;
                    case 'r':
                    servo1.write(positionFermee1);
                    servo2.write(positionFermee2);
                    servo3.write(positionFermee3);
                    Serial.println("All servos are in the closed position.");
                    break;
                    case 'R':
                    servo1.write(positionOuverte1);
                    servo2.write(positionOuverte2);
                    servo3.write(positionOuverte3);
                    Serial.println("All servos are in the open position.");
                    break;
                    default: Serial.println("Unknown command. Use a/A, z/Z, e/E, or r."); break;
                }
                }
                delay(100);
            }
