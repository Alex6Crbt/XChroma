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

        self.data_spectro.save_data(self.data_spectro.avg_i, cycle=1, spectype="zero")
        self.data_spectro.zero = self.data_spectro.avg_i
        _ = input("End I_0, place the protein container!!")
        print("measuring I_ON-->I_OFF")
        # self.controller.send_command("z")
        # time.sleep(20)
        self.reset_servo()
        self.controller.send_command("a")
        self.controller.send_command("z")
        # Loop to save I_on data
        i = 0
        while not self.stop_signal:
            if self.is_paused:
                while self.is_paused and not self.stop_signal:  # Stay in pause loop until resumed or stopped
                    time.sleep(0.1)
                if self.stop_signal:
                    print("Sequence stopping!")
                    break

            i += 1
            self.progress_signal.emit(int(i % 100))  # Emit progress update

            self.data_spectro.lavg.clear()
            time.sleep(1)
            self.data_spectro.save_data(self.data_spectro.avg_i, cycle=1, spectype="off")


        time.sleep(2)
        self.reset_servo()
        self.controller.send_command("z")
        self.data_spectro.lavg.clear()
        time.sleep(10)

        self.data_spectro.save_data(self.data_spectro.avg_i, cycle=1, spectype="static")
        self.data_spectro.static = self.data_spectro.avg_i
        # Update progress

        print("Sequence finished")
        self.finished_signal.emit()  # Emit finished signal
