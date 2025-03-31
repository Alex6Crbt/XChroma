import time
import numpy as np
import pyqtgraph as pg
from PyQt6 import QtCore, uic
from PyQt6.QtWidgets import QMainWindow
from seabreeze.spectrometers import Spectrometer, list_devices
import textwrap


from .arduino_control import ArduinoController
from .data_spectro import DataSpecro

LEN = 2048
# Configuration PyQtGraph (fond sombre)
pg.setConfigOption("background", "#121212")  # Fond
pg.setConfigOption("foreground", "#E0E0E0")  # Texte et lignes

# TODO :
# - Refaire le self.thread = None
# - Refaire le bouton save_data
# ATTENTION LE RESET DES VALEURS EST IMPORTANT !!!
#
class MainWindow(QMainWindow):
    def __init__(self, CustomSequence):
        super().__init__()

        # Load UI from the .ui file
        uic.loadUi("XChroma/ui/MainWindow.ui", self)
        self.setWindowTitle("XChroma")

        # cst
        self.thread = None  # Pas de thread au départ
        self.start_time = time.time()
        # Connect buttons
        self.units_comboBox.currentIndexChanged.connect(self.update_axis_units)
        self.clearplot_pushButton.clicked.connect(self.clear_plot)
        self.clearavg_pushButton.clicked.connect(self.clear_avg)
        self.connectOcean_pushButton.clicked.connect(self.connect_ocean)
        self.connectArduino_pushButton.clicked.connect(self.connect_arduino)
        self.zero_pushButton.clicked.connect(self.set_zero)
        self.static_pushButton.clicked.connect(self.set_static)
        self.clearstatic_pushButton.clicked.connect(self.clear_static)
        self.cleartemporal_pushButton.clicked.connect(self.clear_temp)
        self.launchseq_pushButton.clicked.connect(self.toggle_sequence)
        self.s1_checkBox.clicked.connect(self.toggle_servo1)
        self.s2_checkBox.clicked.connect(self.toggle_servo2)
        self.s3_checkBox.clicked.connect(self.toggle_servo3)
        self.reseta_pushButton.clicked.connect(self.reset_servo)
        # Try connecting to spectro during init
        #
        self.SequenceWorker = CustomSequence
        self.data_spectro = DataSpecro()
        self.connect_ocean()
        self.connect_arduino()

        self.init_plots()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        # self.timer.start(50)
        self.timer.start(
            int(self.delay_doubleSpinBox.value() * 1000)
        )  # Convertir secondes en millisecondes

        self.delay_doubleSpinBox.valueChanged.connect(self.up_delay)
        self.integrationtime_spinBox.valueChanged.connect(self.up_inttime)

    def up_delay(self, value):
        self.timer.setInterval(int(value * 1000))  # Convertir secondes en millisecondes

    def up_inttime(self, value):
        try:
            self.spectro.integration_time_micros(value * 1000)
        except Exception as e:
            print(e)

    def connect_arduino(self):
        self.controller = ArduinoController()
        self.controller.send_command("r")

    def connect_ocean(self):
        print("Init spectrometer")
        devices = list_devices()
        print(f"devices found : {devices}")
        if len(devices) >= 1:
            self.device_found = True
            self.spectro = Spectrometer(devices[0])
            print(f"Connected to {devices[0]}")
            self.spectro.integration_time_micros(
                self.integrationtime_spinBox.value() * 1000
            )  # 0.1 seconds
            self.data_spectro.wavelengths = self.spectro.wavelengths()
            self.data_spectro.intensities = self.spectro.intensities()
            info_text = textwrap.dedent(f"""
            **Spectrometer Information**
            - **Model:** {self.spectro.model}
            - **Serial Number:** {self.spectro.serial_number}
            - **Wavelength Range:** {self.data_spectro.wavelengths[0]:.2f} - {self.data_spectro.wavelengths[-1]:.2f} nm
            - **Samples:** {len(self.data_spectro.wavelengths)}
            """)
            self.info_display.setMarkdown(info_text)

        else:
            self.device_found = False
            print("No device found, click on CONNECT button")
            self.data_spectro.wavelengths = np.linspace(400, 800, LEN)
            self.data_spectro.intensities = np.random.rand(LEN)
            info_text = textwrap.dedent(f"""
            **No Spectrometer Found**
            - **Displaying Synthetic Data**
              - **Wavelength Range:** {self.data_spectro.wavelengths[0]:.2f} - {self.data_spectro.wavelengths[-1]:.2f} nm
              - **Samples:** {len(self.data_spectro.wavelengths)}
            """)
            self.info_display.setMarkdown(info_text)

        print(len(self.data_spectro.wavelengths))
        print(len(self.data_spectro.intensities))
    def init_plots(self):
        self.c1 = self.p1.plot(self.data_spectro.wavelengths, self.data_spectro.intensities)
        self.clear_avg()  # init le plot avg
        self.p1.setLabel("left", "Intensity", units="counts")
        self.p1.setTitle("Raw Data")
        self.p1.enableAutoRange("y", False)
        self.leg1 = self.p1.addLegend()
        self.leg1.addItem(self.c1, "Raw Data")
        self.leg1.addItem(self.c1_avg, "Avg Data")

        # ATTENTION LE RESET DES VALEURS EST IMPORTANT !!!
        # self.zero = np.ones(len(self.xdata))
        self.data_spectro.zero = np.ones(len(self.data_spectro.wavelengths))
        self.clear_static()  # Here self.static is set to [0, ..., 0], et definit le plot avec la référence
        self.leg1.addItem(self.c1_static, "Static signal")

        self.c2 = self.p2.plot(
            self.data_spectro.wavelengths,
            self.data_spectro.compute_absorbance(self.data_spectro.intensities)
        )
        self.p2.setLabel("left", "Absorbance")
        self.p2.setTitle("Absorbance")
        self.p2.enableAutoRange("y", False)

        self.c3 = self.p3.plot(
            self.data_spectro.wavelengths,
            self.data_spectro.compute_absorbance(self.data_spectro.intensities)
        )
        self.p3.setLabel("left", "Absorbance")
        # self.p3.setTitle("Raw Data")
        self.p3.enableAutoRange("y", False)
        self.leg3 = self.p3.addLegend()
        self.leg3.addItem(self.c3, "Intensity Data")
        # self.leg3.addItem(self.c1_avg, 'Absorbance Data')

        self.set_roi()

        self.clear_temp()
        self.p4.setClipToView(True)
        self.c4 = self.p4.plot()
        self.p4.setLabel("bottom", "Time", units="s")
        self.p4.setLabel("left", "Absorbance")

        self.leg4 = self.p4.addLegend()
        self.leg4.addItem(self.c4, f"Absorbance {self.roi_pos}")
        # print(self.leg4)
        self.update_axis_units()

    def update_axis_units(self):
        id = self.units_comboBox.currentIndex()
        if id == 0:
            # Revenir à l'échelle des longueurs d'onde en nm
            self.p1.setLabel("bottom", "Wavelength", units="nm")
            self.p2.setLabel("bottom", "Wavelength", units="nm")
            self.p3.setLabel("bottom", "Wavelength", units="nm")
            self.data_spectro.scaledxdata = self.data_spectro.wavelengths

            # Update de la ROI
            self.region.setBounds([np.min(self.data_spectro.scaledxdata), np.max(self.data_spectro.scaledxdata)])
            self.region.setRegion( self.data_spectro.scaledxdata[self.roi_idxs])

        elif id == 2:
            # Convertir de nm à THz (c = 3e8 m/s)
            self.p1.setLabel("bottom", "Frequency", units="THz")
            self.p2.setLabel("bottom", "Frequency", units="THz")
            self.p3.setLabel("bottom", "Frequency", units="THz")
            self.data_spectro.scaledxdata = 3e5 / self.data_spectro.wavelengths  # Conversion nm -> THz
            self.region.setBounds([np.min(self.data_spectro.scaledxdata), np.max(self.data_spectro.scaledxdata)])
            self.region.setRegion(self.data_spectro.scaledxdata[self.roi_idxs])

        elif id == 1:
            # Convertir de nm à eV (E = hc/λ, h*c = 1240 eV·nm)
            self.p1.setLabel("bottom", "Energy", units="eV")
            self.p2.setLabel("bottom", "Energy", units="eV")
            self.p3.setLabel("bottom", "Energy", units="eV")
            self.data_spectro.scaledxdata = 1240 / self.data_spectro.wavelengths  # Conversion nm -> eV
            self.region.setBounds([np.min(self.data_spectro.scaledxdata), np.max(self.data_spectro.scaledxdata)])
            self.region.setRegion(self.data_spectro.scaledxdata[self.roi_idxs])

        # Mettre à jour les données du graphique
        self.c1.setData(self.data_spectro.scaledxdata, self.data_spectro.intensities, pen=(154, 109, 198))
        self.c2.setData(self.data_spectro.scaledxdata, self.data_spectro.compute_absorbance(self.data_spectro.intensities))
        self.c3.setData(self.data_spectro.scaledxdata, self.data_spectro.intensities)

    def uplot_1(self):

        if self.static_checkBox.isChecked():
            static = self.data_spectro.static
            self.c1_static.setData(self.data_spectro.scaledxdata, static, pen=(134, 79, 178))
        else:
            static = np.zeros(len(self.data_spectro.wavelengths))
        # ICI UPDATE DU TRUC LAVG
        if self.avg_checkBox.isChecked():
            self.c1_avg.setData(
                self.data_spectro.scaledxdata, self.data_spectro.avg_i - static, pen=(255, 255, 0)
            )  # Couleur Jaune
        else:
            self.c1_avg.clear()
        self.c1.setData(self.data_spectro.scaledxdata, self.data_spectro.intensities, pen=(128, 128, 128))

    def uplot_2(self):
        if self.static_checkBox.isChecked():
            static = self.data_spectro.static
        else:
            static = np.zeros(len(self.data_spectro.wavelengths))

        if self.avg_checkBox.isChecked():
            data = self.data_spectro.avg_i
        else:
            data = self.data_spectro.intensities

        absorbance = self.data_spectro.compute_absorbance(data, static=static)
        self.c2.setData(self.data_spectro.scaledxdata, absorbance)

    def uplot_3(self):
        if self.static_checkBox.isChecked():
            static = self.data_spectro.static
        else:
            static = np.zeros(len(self.data_spectro.wavelengths))

        if self.avg_checkBox.isChecked():
            data = self.data_spectro.avg_i
        else:
            data = self.data_spectro.intensities

        absorbance = self.data_spectro.compute_absorbance(data, static=static)
        self.c3.setData(self.data_spectro.scaledxdata, absorbance, pen=(154, 109, 198))

    def uplot_4(self):
        if self.static_checkBox.isChecked():
            static = self.data_spectro.static
        else:
            static = np.zeros(len(self.data_spectro.wavelengths))

        if self.avg_checkBox.isChecked():
            data = self.data_spectro.avg_i
        else:
            data = self.data_spectro.intensities
        idxs, temp_dat, times_temp_dat =  self.data_spectro.temporal_abs(self.region.getRegion(), data, self.data_spectro.scaledxdata, static=static, zero=self.data_spectro.zero)
        self.roi_idxs = idxs

        legtxt = self.leg4.getLabel(self.c4)
        legtxt.setText(
            f"Absorbance [{self.data_spectro.wavelengths[idxs[0]]:0.1f} nm, {self.data_spectro.wavelengths[idxs[1]]:0.1f} nm]"
        )
        self.c4.setData(np.array(times_temp_dat)-self.start_time, temp_dat)

    def update_plots(self):
        if self.device_found == True:
            self.data_spectro.intensities = self.spectro.intensities()
        else:
            self.data_spectro.intensities = self.data_spectro.synthetic_data()
        self.data_spectro.update_moving_avg(avg_window = self.avgspinBox.value())
        self.uplot_1()
        self.uplot_2()
        self.uplot_3()
        self.uplot_4()

    def clear_plot(self):
        self.p1.clear()
        self.p2.clear()
        self.p3.clear()
        self.p4.clear()
        self.init_plots()

    def set_zero(self):
        if self.avg_checkBox.isChecked():
            self.data_spectro.zero = self.data_spectro.avg_i
        else:
            self.data_spectro.zero = self.data_spectro.intensities

    def set_static(self):
        if self.avg_checkBox.isChecked():
            self.data_spectro.static = self.data_spectro.avg_i
        else:
            self.data_spectro.static = self.data_spectro.intensities

    def set_roi(self):
        self.roi_pos = (590, 610)

        self.region = pg.LinearRegionItem(
            values=self.roi_pos
        )  # , bounds = [np.min(self.xdata), np.max(self.xdata)])
        self.roi_idxs = np.argmin(
            np.abs(self.data_spectro.wavelengths[:, None] - np.array(self.region.getRegion())), axis=0
        )

        self.p3.addItem(self.region)

    def clear_avg(self):
        # self.lavg = []
        self.data_spectro.lavg.clear()
        try:
            self.c1_avg.clear()
        except:
            pass
        self.c1_avg = self.p1.plot(pen=(255, 255, 0))

    def clear_static(self):
        # self.static = np.zeros(len(self.xdata))
        self.data_spectro.static = np.zeros(len(self.data_spectro.wavelengths))
        try:
            self.c1_static.clear()
        except:
            pass
        self.c1_static = self.p1.plot()

    def clear_temp(self):
        self.data_spectro.temp_dat.clear()
        self.data_spectro.times_temp_dat.clear()
        self.start_time = time.time()


    def toggle_servo1(self):
        # self.controller.send_command("a")  # Commande pour activer le servo 1
        command = "a" if self.s1_checkBox.isChecked() else "A"
        self.controller.send_command(command)

    def toggle_servo2(self):
        # self.controller.send_command("z")  # Commande pour activer le servo 1
        command = "z" if self.s2_checkBox.isChecked() else "Z"
        self.controller.send_command(command)

    def toggle_servo3(self):
        # self.controller.send_command("e")  # Commande pour activer le servo 3
        # self.controller.send_command("e")  # Commande pour activer le servo 1
        command = "e" if self.s3_checkBox.isChecked() else "E"
        self.controller.send_command(command)

    def reset_servo(self):
        self.controller.send_command("r")
        self.s1_checkBox.setChecked(False)
        self.s2_checkBox.setChecked(False)
        self.s3_checkBox.setChecked(False)

    def closeEvent(self, event):
        """
        Cette méthode est appelée lors de la fermeture de la fenêtre principale.
        Ici, nous fermons la connexion avec l'Arduino avant de quitter l'application.
        """
        # df = pd.DataFrame(self.data_buffer)  # Convertir le tampon en DataFrame
        # df.to_csv("data.csv", mode="a", header=False, index=False)  # Append au fichier

        if self.controller.arduino:  # Vérifie si l'arduino est connecté
            self.controller.send_command("r")

            self.controller.arduino.close()  # Ferme la connexion série avec l'Arduino
            print("Connexion Arduino fermée.")

        event.accept()  # Accepte la fermeture de la fenêtre

    def toggle_sequence(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()  # Arrêter proprement
            self.launchseq_pushButton.setText("Launch Sequence")
        else:
            self.thread = self.SequenceWorker(self.controller, self.data_spectro)
            self.thread.progress_signal.connect(
                self.update_progress_bar
            )  # Connecte la mise à jour de la ProgressBar
            self.thread.finished_signal.connect(
                lambda: self.launchseq_pushButton.setText("Launch Sequence")
            )
            self.launchseq_pushButton.setText("Stop")
            self.thread.start()

    def update_progress_bar(self, progress):
        """Mettre à jour la ProgressBar avec la progression reçue"""
        self.progressBar.setValue(
            progress
        )  # Mise à jour de la valeur de la ProgressBar
