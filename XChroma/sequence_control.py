from PyQt6.QtCore import QThread, pyqtSignal
import time


class SequenceWorker(QThread):
    finished_signal = pyqtSignal() #: To send end signal to the MainWindow
    progress_signal = pyqtSignal(int)  #: To send progress updates to the MainWindow

    def __init__(self, arduino_controller, data_spectro):
        super().__init__()
        self.controller = arduino_controller  # Store the reference to ArduinoController instance
        self.data_spectro = data_spectro
        self.stop_signal = False  # Flag to stop the thread
        self.is_paused = False

    def run(self):
        pass

    def request_stop(self):
        """Request the thread to stop."""
        self.stop_signal = True
        print("Stopping !")
        self.progress_signal.emit(int(100))

    def toggle_servo(self, command, delay=1):
        """Toggle a servo by sending a specific command."""
        self.controller.send_command(command)
        time.sleep(delay)

    def reset_servo(self, delay=1):
        """Reset all servo's to their respective initial positions."""
        self.controller.send_command("r")
        time.sleep(delay)

    def pause_resume(self):
        self.is_paused = not self.is_paused
