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

        # Main sequence loop
        for i in range(20):
            if self.stop_signal:
                print("Sequence stopped!")
                break

            print(f"Step {i + 1}/20:")
            self.reset_servo()
            self.data_spectro.lavg.clear()
            time.sleep(5)

            self.data_spectro.save_data(self.data_spectro.avg_i, cycle=i, spectype="static")
            self.data_spectro.static = self.data_spectro.avg_i

            self.controller.send_command("a")
            self.data_spectro.lavg.clear()
            time.sleep(5)

            self.controller.send_command("z")

            # Loop to save I_on data
            for l in range(15):
                self.data_spectro.lavg.clear()
                time.sleep(1)
                self.data_spectro.save_data(self.data_spectro.avg_i, cycle=i, spectype="on")

            self.controller.send_command("Z")
            time.sleep(5)
            self.controller.send_command("e")

            # Loop to save I_off data
            for l in range(45):
                self.data_spectro.lavg.clear()
                time.sleep(1)
                self.data_spectro.save_data(self.data_spectro.avg_i, cycle=i, spectype="off")
            time.sleep(2)

            # Update progress
            self.progress_signal.emit(int((i + 1) * 5))

        print("Sequence finished")
        self.finished_signal.emit()  # Emit finished signal
