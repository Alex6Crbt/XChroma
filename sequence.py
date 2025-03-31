from XChroma.sequence_control import SequenceWorker
import time

class Sequence(SequenceWorker):
    def run(self):
        print("Sequence started")
        self.reset_servo()
        self.controller.send_command("a")

        # First user input prompt
        _ = input("I_0, place the water container!!")
        self.data_spectro.lavg.clear()
        time.sleep(10)

        self.data_spectro.save_data(self.data_spectro.avg_i, cycle=0, spectype="zero")
        self.data_spectro.zero = self.data_spectro.avg_i
        _ = input("End I_0, place the protein container!!")
        print("measuring I_ON-->I_OFF")
        self.controller.send_command("z")
        time.sleep(20)
        self.reset_servo()
        self.controller.send_command("a")
        self.controller.send_command("e")
        # Loop to save I_on data
        for i in range(100):
            self.data_spectro.lavg.clear()
            time.sleep(0.3)
            self.data_spectro.save_data(self.data_spectro.avg_i, cycle=0, spectype="on")
            self.progress_signal.emit(int((i + 1)))

        time.sleep(2)
        self.reset_servo()
        self.controller.send_command("a")
        self.controller.send_command("e")
        self.data_spectro.lavg.clear()
        time.sleep(10)

        self.data_spectro.save_data(self.data_spectro.avg_i, cycle=0, spectype="static")
        # Update progress

        print("Sequence finished")
        self.finished_signal.emit()  # Emit finished signal
