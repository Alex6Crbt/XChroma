import sys
from PyQt6.QtWidgets import QApplication
from XChroma.app import MainWindow
from sequence import SequenceQY, SequenceFatigue, SequenceBunch

sequence_dict = {
    "Sequence QY": {"class": SequenceQY, "args": {"servo_letter": str, "delay": int}},
    "Sequence Photofatigue": {"class": SequenceFatigue, "args": {"param1": int, "param2": int}},
    "Sequence Bunch": {"class": SequenceBunch, "args": {}},
}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(sequence_dict)
    window.show()
    sys.exit(app.exec())
