from XChroma.sequence_control import SequenceWorker
import time


class SequenceQY(SequenceWorker):
    def __init__(self, controller, data_spectro, servo_letter="z", delay=1):
        super().__init__(controller, data_spectro)
        self.servo_letter = servo_letter  # String
        self.delay = delay  # Integer
        print(f"params : {servo_letter}, {delay}")
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
        self.controller.send_command(self.servo_letter)
        # Loop to save I_on data
        i = 0
        while not self.stop_signal:
            if self.is_paused:
                while (
                    self.is_paused and not self.stop_signal
                ):  # Stay in pause loop until resumed or stopped
                    time.sleep(0.1)
                if self.stop_signal:
                    print("Sequence stopping!")
                    break

            i += 1
            self.progress_signal.emit(int(i % 100))  # Emit progress update

            self.data_spectro.lavg.clear()
            time.sleep(self.delay)
            spectype = "off" if self.servo_letter == "z" else "on" if self.servo_letter == "e" else "none"
            self.data_spectro.save_data(
                self.data_spectro.avg_i, cycle=1, spectype=spectype
            )

        time.sleep(2)
        self.reset_servo()
        self.controller.send_command(self.servo_letter)
        self.data_spectro.lavg.clear()
        time.sleep(10)

        self.data_spectro.save_data(self.data_spectro.avg_i, cycle=1, spectype="static")
        self.data_spectro.static = self.data_spectro.avg_i
        # Update progress

        print("Sequence finished")
        self.finished_signal.emit()  # Emit finished signal


class SequenceBunch(SequenceWorker):
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
            while self.is_paused:
                time.sleep(0.1)  # Non-blocking wait

            print(f"Step {i + 1}/20:")
            self.reset_servo()
            self.data_spectro.lavg.clear()
            time.sleep(5)

            self.data_spectro.save_data(
                self.data_spectro.avg_i, cycle=i, spectype="static"
            )
            self.data_spectro.static = self.data_spectro.avg_i

            self.controller.send_command("a")
            self.data_spectro.lavg.clear()
            time.sleep(5)

            self.controller.send_command("z")

            # Loop to save I_on data
            for l in range(15):
                self.data_spectro.lavg.clear()
                time.sleep(1)
                self.data_spectro.save_data(
                    self.data_spectro.avg_i, cycle=i, spectype="on"
                )

            self.controller.send_command("Z")
            time.sleep(5)
            self.controller.send_command("e")

            # Loop to save I_off data
            for l in range(45):
                self.data_spectro.lavg.clear()
                time.sleep(1)
                self.data_spectro.save_data(
                    self.data_spectro.avg_i, cycle=i, spectype="off"
                )
            time.sleep(2)

            # Update progress
            self.progress_signal.emit(int((i + 1) * 5))

        print("Sequence finished")
        self.finished_signal.emit()  # Emit finished signal


class SequenceFatigue(SequenceWorker):
    def __init__(self, controller, data_spectro, delay1=10, delay2=20):
        super().__init__(controller, data_spectro)
        self.delay1 = delay1  # String
        self.delay2 = delay2  # Integer
        self.servo_letter = servo_letter

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
        time.sleep(2)
        print("Return full form")
        self.controller.send_command("z")
        time.sleep(30)
        print("Start Cycle !")
        self.reset_servo()
        self.controller.send_command("a")
        # Loop to save I_on data
        i = 0
        while not self.stop_signal:
            if self.is_paused:
                while (
                    self.is_paused and not self.stop_signal
                ):  # Stay in pause loop until resumed or stopped
                    time.sleep(0.1)
                if self.stop_signal:
                    print("Sequence stopping!")
                    break

            i += 1
            self.progress_signal.emit(int(i % 100))  # Emit progress update

            self.controller.send_command("z")
            time.sleep(self.param1)
            self.controller.send_command("Z")
            self.data_spectro.lavg.clear()
            time.sleep(10)
            self.data_spectro.save_data(self.data_spectro.avg_i, cycle=i, spectype="on")

            self.controller.send_command("e")
            time.sleep(self.param2)
            self.controller.send_command("E")
            self.data_spectro.lavg.clear()
            time.sleep(10)
            self.data_spectro.save_data(self.data_spectro.avg_i, cycle=i, spectype="off")

            self.reset_servo()
            self.data_spectro.lavg.clear()
            time.sleep(10)
            self.data_spectro.save_data(self.data_spectro.avg_i, cycle=i, spectype="static")
            self.data_spectro.static = self.data_spectro.avg_i


        time.sleep(2)
        self.reset_servo()
        # Update progress

        print("Sequence finished")
        self.finished_signal.emit()  # Emit finished signal
