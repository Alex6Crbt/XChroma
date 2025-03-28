import serial
import serial.tools.list_ports

class ArduinoController:
    def __init__(self):
        self.arduino = None
        self.arduino_port = None
        self.connect_arduino()

    def connect_arduino(self):
        """Find and connect to an available Arduino device."""
        def find_arduino():
            """Search for Arduino device in available serial ports."""
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if any(keyword in port.description or keyword in port.device for keyword in ["Arduino", "CH340", "ttyUSB", "ttyACM", "cu.usbmodem"]):
                    return port.device
            return None

        self.arduino_port = find_arduino()
        if self.arduino_port:
            try:
                self.arduino = serial.Serial(self.arduino_port, 9600, timeout=1)
                print("Arduino connected successfully.")
            except serial.SerialException as e:
                print(f"Failed to connect to Arduino: {e}")
        else:
            print("Arduino not found.")

    def send_command(self, command):
        """Send a command to the Arduino device."""
        if self.arduino:
            self.arduino.write(command.encode())
            # Uncomment the following block if you want to read the response:
            # while self.arduino.in_waiting > 0:
            #     response = self.arduino.readline().decode('utf-8').strip()
            #     print(response)
        else:
            print("Arduino is not connected.")
