import time
import numpy as np
import pyqtgraph as pg
from PyQt6 import QtCore, uic
from PyQt6.QtGui import QFontDatabase, QIcon, QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMainWindow
from seabreeze.spectrometers import Spectrometer, list_devices
import textwrap
import os

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

        font_folder = "XChroma/ui/fonts"
        font_folder_path = os.path.abspath(font_folder)

        if not os.path.exists(font_folder_path):
            print(f"Font folder not found: {font_folder_path}")
        else:
            for font_file in os.listdir(font_folder_path):
                if font_file.endswith(".ttf"):  # Only load TTF fonts
                    font_path = os.path.join(font_folder_path, font_file)
                    font_id = QFontDatabase.addApplicationFont(font_path)

                    if font_id != -1:
                        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                        # print(f"Successfully loaded font: {font_family} ({font_file})")
                    else:
                        print(f"Failed to load font: {font_file}")
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
        self.resetseq_pushButton.clicked.connect(self.reset_sequence)
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
        r"""
        Sets the time interval between two acquisitions.
        This affects both the display refresh rate and the minimum time between two redundant saves.

        This function is triggered when the value of `delay_doubleSpinBox` changes.

        Parameters
        ----------
        value : int
            timer interval.

        Returns
        -------
        None.

        """
        self.timer.setInterval(int(value * 1000))  # Convertir secondes en millisecondes

    def up_inttime(self, value):
        r"""
        Sets the integration time for the spectrometer.

        This function is triggered when the value of `integrationtime_spinBox` changes.

        Parameters
        ----------
        value : int or float
            Integration time in milliseconds.

        Returns
        -------
        None

        """
        try:
            self.spectro.integration_time_micros(value * 1000)
        except Exception as e:
            print(e)

    def connect_arduino(self):
        r"""
        Initializes and connects to the Arduino controller.

        Returns
        -------
        None.

        """
        self.controller = ArduinoController()
        self.controller.send_command("r")

    def connect_ocean(self):
        r"""
        Connects to an Ocean Optics spectrometer and initializes it.

        This function detects connected spectrometer devices, establishes a connection
        to the first available device, and initializes its integration time. If no
        spectrometer is found, it generates synthetic data for display.

        Returns
        -------
        None.

        """
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
        """
        Initializes the PyQtGraph plots for displaying spectrometer data.

        Returns
        -------
        None.

        """
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
        r"""
        Updates the x-axis label based on the selected unit.

        This function checks the current selection of `units_comboBox` and updates
        the x-axis labels of multiple plots accordingly.
        Depending on the selected unit, the x-axis could be labeled with:

        - **Wavelength (nm)**: For normal people.
        - **Energy (eV)**: For energy enthusiasts.
        - **Frequency (THz)**: Who use this ?

        Returns
        -------
        None.

        """
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
        """
        Updates the first plot with spectrometer data.

        This function updates Plot 1 based on the current settings:

        - If the "Static" checkbox is checked, the static data is plotted with a custom color.
        - If the "Avg" checkbox is checked, the average intensity data is plotted, adjusted for static values, with a yellow line.
        - If neither checkbox is selected, the static plot is cleared, and only the raw intensity data is shown.

        What is displayed:

        - **Raw Data**: A plot of the intensity values against the wavelength (scaled data) with a gray line.
        - **Static Data**: If enabled, a plot of the static values against the wavelength with a purple line.
        - **Average Data**: If enabled, a plot of the average intensity values with the static data subtracted, displayed in yellow.

        Returns
        -------
        None.

        """

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
        r"""
        Updates the second plot with absorbance data.

        This function updates Plot 2 (For the Spetral Tab) based on the current settings:

        - If the "Static" checkbox is checked, the static data is considered when calculating absorbance.
        - If the "Avg" checkbox is checked, the average intensity is used for absorbance calculation.
        - If the "Avg" checkbox is not checked, the raw intensity is used instead.

        The absorbance is calculated directly with the compute_absorbance method of the Dataclass

        What is displayed:

        - **Absorbance Data**: A plot of absorbance values.

        Returns
        -------
        None.

        """
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
        r"""
        Updates the second plot with absorbance data.

        This function updates Plot 3 (For the Temporal Tab) based on the current settings:

        - If the "Static" checkbox is checked, the static data is considered when calculating absorbance.
        - If the "Avg" checkbox is checked, the average intensity is used for absorbance calculation.
        - If the "Avg" checkbox is not checked, the raw intensity is used instead.

        The absorbance is calculated directly with the compute_absorbance method of the Dataclass

        What is displayed:

        - **Absorbance Data**: A plot of absorbance values.

        Returns
        -------
        None.

        """
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
        r"""
        Updates the Plot 4 with temporal absorbance data.

        This function updates Plot 4 based on the current settings:

        - If the "Static" checkbox is checked, the static data is considered when calculating temporal absorbance.
        - If the "Avg" checkbox is checked, the average intensity is used for the absorbance calculation.
        - If the "Avg" checkbox is not checked, the raw intensity is used instead.

        The absorbance is calculated over a selected region, and the time series data is plotted accordingly.

        What is displayed:

        - **Temporal Absorbance Data**: A plot of temporal absorbance over the selected wavelength region. The x-axis represents time (relative to the start time), and the y-axis represents the absorbance values.

        Returns
        -------
        None.

        """
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
        r"""
        Updates all plots with the latest data.

        This function checks whether a device is connected:

        - If a device is found, it fetches the latest intensity data from the spectrometer.
        - If no device is found, it uses synthetic data for the plots.

        After updating the intensity data, the function:

        - Updates the moving average of the intensity data based on the value from the `avgspinBox`.
        - Updates all four plots (`uplot_1`, `uplot_2`, `uplot_3`, and `uplot_4`) with the latest data.

        Returns
        -------
        None.

        """
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
        r"""
        Clear plots, and init them back

        Returns
        -------
        None.

        """
        self.p1.clear()
        self.p2.clear()
        self.p3.clear()
        self.p4.clear()
        self.init_plots()

    def set_zero(self):
        r"""
        Sets the baseline (zero) intensity data in the `data_spectro` class.

        This function updates the `zero` attribute in `data_spectro` based on the current
        checkbox selection:

        - If the "Avg" checkbox is checked, the baseline is set to the average intensity data.
        - If the "Avg" checkbox is not checked, the baseline is set to the raw intensity data.


        Returns
        -------
        None.

        """
        if self.avg_checkBox.isChecked():
            self.data_spectro.zero = self.data_spectro.avg_i
        else:
            self.data_spectro.zero = self.data_spectro.intensities

    def set_static(self):
        r"""
        Sets the static intensity data in the `data_spectro` class.

        This function updates the `static` attribute in the `data_spectro` class based on
        the current checkbox selection:

        - If the "Avg" checkbox is checked, the static data is set to the average intensity data (`avg_i`).
        - If the "Avg" checkbox is not checked, the static data is set to the raw intensity data (`intensities`).

        The `static` value is used for baseline correction and further data analysis.

        Returns
        -------
        None.

        """
        if self.avg_checkBox.isChecked():
            self.data_spectro.static = self.data_spectro.avg_i
        else:
            self.data_spectro.static = self.data_spectro.intensities

    def set_roi(self):
        r"""
        Set the Region Of Interest, also update it if units are changed

        Returns
        -------
        None.

        """
        self.roi_pos = (590, 610)

        self.region = pg.LinearRegionItem(
            values=self.roi_pos
        )  # , bounds = [np.min(self.xdata), np.max(self.xdata)])
        self.roi_idxs = np.argmin(
            np.abs(self.data_spectro.wavelengths[:, None] - np.array(self.region.getRegion())), axis=0
        )

        self.p3.addItem(self.region)

    def clear_avg(self):
        r"""
        Clear the averaged data stored in the data_spectro class

        Returns
        -------
        None.

        """
        # self.lavg = []
        self.data_spectro.lavg.clear()
        try:
            self.c1_avg.clear()
        except:
            pass
        self.c1_avg = self.p1.plot(pen=(255, 255, 0))

    def clear_static(self):
        r"""
        Clear the static data stored in the data_spectro class

        Returns
        -------
        None.

        """
        # self.static = np.zeros(len(self.xdata))
        self.data_spectro.static = np.zeros(len(self.data_spectro.wavelengths))
        try:
            self.c1_static.clear()
        except:
            pass
        self.c1_static = self.p1.plot()

    def clear_temp(self):
        r"""
        Clear the temporal averaged data stored in the data_spectro class

        Returns
        -------
        None.

        """
        self.data_spectro.temp_dat.clear()
        self.data_spectro.times_temp_dat.clear()
        self.start_time = time.time()


    def toggle_servo1(self):
        r"""
        Toggles the state of Servo 1 based on the checkbox status.

        Returns
        -------
        None.

        """
        # self.controller.send_command("a")  # Commande pour activer le servo 1
        command = "a" if self.s1_checkBox.isChecked() else "A"
        self.controller.send_command(command)

    def toggle_servo2(self):
        r"""
        Toggles the state of Servo 2 based on the checkbox status.

        Returns
        -------
        None.

        """
        # self.controller.send_command("z")  # Commande pour activer le servo 1
        command = "z" if self.s2_checkBox.isChecked() else "Z"
        self.controller.send_command(command)

    def toggle_servo3(self):
        r"""
        Toggles the state of Servo 3 based on the checkbox status.

        Returns
        -------
        None.

        """
        # self.controller.send_command("e")  # Commande pour activer le servo 3
        # self.controller.send_command("e")  # Commande pour activer le servo 1
        command = "e" if self.s3_checkBox.isChecked() else "E"
        self.controller.send_command(command)

    def reset_servo(self):
        r"""
        Reset the state of all Servo's and the checkbox status.

        Returns
        -------
        None.

        """
        self.controller.send_command("r")
        self.s1_checkBox.setChecked(False)
        self.s2_checkBox.setChecked(False)
        self.s3_checkBox.setChecked(False)

    def closeEvent(self, event):
        r"""
        Handles the event when the main window is closed.

        This method is called when the main window is closed. It performs cleanup tasks
        before the application exits:

        - If an Arduino is connected, it sends a command to the Arduino to signal the
          termination of communication.
        - Closes the serial connection with the Arduino to safely disconnect.

        Additionally, it could optionally save data to a CSV file, though this functionality
        is currently commented out.

        Parameters
        ----------
        event : QCloseEvent
            The close event triggered when the user attempts to close the window.

        Returns
        -------
        None.
        """
        # df = pd.DataFrame(self.data_buffer)  # Convertir le tampon en DataFrame
        # df.to_csv("data.csv", mode="a", header=False, index=False)  # Append au fichier

        if self.controller.arduino:  # Vérifie si l'arduino est connecté
            self.controller.send_command("r")

            self.controller.arduino.close()  # Ferme la connexion série avec l'Arduino
            print("Connexion Arduino fermée.")

        event.accept()  # Accepte la fermeture de la fenêtre

    def toggle_sequence(self):
        r"""
        Starts, pauses, or resumes the sequence execution.

        - If a sequence thread is running:

            - Toggles between pausing and resuming.
            - Updates the button text and icon accordingly.

        - If no sequence is running:

            - Creates a new `SequenceWorker` thread to handle the sequence.
            - Connects thread signals for progress updates and completion handling.
            - Starts the thread and updates the button to indicate a running sequence.

        Returns
        -------
        None
        """
        if self.thread and self.thread.isRunning():
            self.thread.pause_resume()
            if self.thread.is_paused:
                self.launchseq_pushButton.setText("Resume")
                self.launchseq_pushButton.setIcon(QIcon("XChroma/ui/icons/play.svg"))  # Set Play icon
            else:
                self.launchseq_pushButton.setText("Paused")
                self.launchseq_pushButton.setIcon(QIcon("XChroma/ui/icons/pause.svg"))  # Set Pause icon
        else:
            self.thread = self.SequenceWorker(self.controller, self.data_spectro)
            self.thread.progress_signal.connect(self.update_progress_bar)
            self.thread.finished_signal.connect(self.sequence_finished)
            self.launchseq_pushButton.setText("Paused")
            self.launchseq_pushButton.setIcon(QIcon("XChroma/ui/icons/pause.svg"))  # Set Pause icon
            self.thread.start()

    def reset_sequence(self):
        r"""
        Stops and resets the sequence execution.

        If a sequence thread is running, it sends a stop request to ensure the
        sequence is properly terminated before resetting.

        Returns
        -------
        None
        """
        if self.thread:
            self.thread.request_stop()  # Ensure the thread stops before resetting


    def sequence_finished(self):
        r"""
        Handles actions to perform when a sequence is finished.

        - Resets the button text and icon to indicate that the sequence has stopped.

        Returns
        -------
        None
        """
        self.launchseq_pushButton.setText("Launch Sequence")
        self.launchseq_pushButton.setIcon(QIcon("XChroma/ui/icons/play.svg"))

    def update_progress_bar(self, progress):
        r"""
        Updates the progress bar based on the received progress value.

        Parameters
        ----------
        progress : int
            The current progress value (typically between 0 and 100).

        Returns
        -------
        None
        """
        self.progressBar.setValue(
            progress
        )  # Mise à jour de la valeur de la ProgressBar

    def mousePressEvent(self, event):
        if self.label_10.rect().contains(event.pos()):
            QDesktopServices.openUrl(QUrl("https://github.com/Alex6Crbt/XChroma"))
        super().mousePressEvent(event)
