import serial
import serial.tools.list_ports

class ArduinoController:
    def __init__(self):
        self.arduino = None
        self.arduino_port = None
        self.connect_arduino()

    def connect_arduino(self):
        """Find and connect to an available Arduino device on Windows or macOS."""
        def find_arduino():
            """Search for an Arduino device in available serial ports."""
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if any(keyword.lower() in (port.description or '').lower() or
                       keyword.lower() in (port.device or '').lower()
                       for keyword in ["arduino", "ch340", "ttyusb", "ttyacm", "cu.usbmodem"]):
                    return port.device

                # For Windows, ensure we get the correct COM port
                if "COM" in port.device.upper():
                    try:
                        test_serial = serial.Serial(port.device, 9600, timeout=1)
                        test_serial.close()
                        return port.device
                    except serial.SerialException:
                        continue
            return None

        self.arduino_port = find_arduino()
        if not self.arduino_port:
            print("Arduino not found. Ensure it is connected and try again.")
            return

        try:
            self.arduino = serial.Serial(self.arduino_port, 9600, timeout=1)
            print(f"Arduino connected successfully on {self.arduino_port}.")
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino on {self.arduino_port}: {e}")
            self.arduino = None


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
