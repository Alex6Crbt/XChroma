from collections import deque
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
import os
from datetime import datetime
import time


EPS = 1e-10  # Petite constante pour éviter les divisions par zéro
LEN = 2048  # Taille par défaut des données


@dataclass
class DataSpecro:
    wavelengths: np.ndarray = None
    intensities: np.ndarray = None
    scaledxdata: np.ndarray = None
    zero: np.ndarray = field(default_factory=lambda: np.ones(LEN))  # Valeur par défaut
    static: np.ndarray = field(default_factory=lambda: np.zeros(LEN))  # Par défaut à zéro
    lavg: deque = field(default_factory=deque)  # Utilisation d'une deque pour gérer la fenêtre glissante
    avg_i: np.ndarray = None
    temp_dat: deque = field(default_factory=deque)#lambda: deque(maxlen=42))
    times_temp_dat: deque = field(default_factory=deque)#lambda: deque(maxlen=42))

    def compute_absorbance(self, intensities: np.ndarray, static: np.ndarray = None, zero: np.ndarray = None) -> np.ndarray:

        # Utiliser les valeurs de la classe si les arguments ne sont pas fournis
        static = self.static if static is None else static
        zero = self.zero if zero is None else zero

        num = intensities - static
        den = np.maximum(zero - static, EPS)  # Éviter division par zéro
        absorbance = -np.log10(np.maximum(num / den, EPS))  # Éviter log(0) ou log(négatif)

        return absorbance

    def update_moving_avg(self, avg_window: int = 10):
        """
        Met à jour la moyenne glissante de `intensities` si appelé. Utilise une deque pour optimiser la gestion de la fenêtre.
        """
        self.avg_window = avg_window  # Mise à jour de la taille de la fenêtre

        # Si la fenêtre glissante est plus grande que l'historique actuel
        if len(self.lavg) < self.avg_window:
            self.lavg.append(self.intensities)
        elif len(self.lavg) > self.avg_window:
            for i in range(len(self.lavg) - self.avg_window):
                self.lavg.popleft()  # O(1) en moyenne, ce qui est plus rapide que pop(0)
        else:
            # Supprime la première entrée pour faire de la place à la nouvelle donnée
            self.lavg.popleft()  # O(1) en moyenne, ce qui est plus rapide que pop(0)
            self.lavg.append(self.intensities)

        # Calcul de la moyenne glissante
        self.avg_i = np.mean(self.lavg, axis=0)


    def temporal_abs(self, roi: tuple, ydata: np.ndarray, xdata: np.ndarray, static: np.ndarray, zero: np.ndarray,):
        # self.xdata[:, None] : Ajoute une nouvelle dmension à self.xdata pour permettre la diffusion (broadcasting). Cela crée une matrice où chaque ligne correspond à un élément de self.xdata.
        idxs = np.argmin(np.abs(xdata[:, None] - np.array(roi)), axis=0)
        # pour les cas ou les x sont inversés avec le changement d'unités.'
        idxs = np.sort(idxs)
        absorbance = self.compute_absorbance(intensities=ydata[idxs[0] : idxs[1] + 1], static=static[idxs[0] : idxs[1] + 1], zero=zero[idxs[0] : idxs[1] + 1])
        self.times_temp_dat.append(time.time())
        self.temp_dat.append(np.mean(absorbance))
        return idxs, list(self.temp_dat), list(self.times_temp_dat)


    def synthetic_data(self):
        """
        Create synthetic data
        """
        synth = 0.1+ 0.25 * np.abs(np.random.randn(LEN)) + 10 * (np.sin((time.time()) / 10)) ** 2* ( np.exp( -((self.wavelengths - np.mean(self.wavelengths)) ** 2) / (0.05 * np.std(self.wavelengths) ** 2)))
        return synth

    def save_data(self, data: np.ndarray, cycle: int, spectype: str, csv_path: str = "Spectrums.csv"):
        """
        Saves spectral data to a CSV file, including a timestamp, cycle numbr,
        and measurement type (on/off/static/zero).

        The function will first check if the CSV file exists. If it doesn't, it will
        create a new file and write the necessary headers (timestamp, cycle, type, and wavelengths).
        Then, it appends a new row containing the timestamp, cycle, measurement type,
        and absorbance or intensity data.

        Parameters
        ----------
        data : np.ndarray
            Absorbance or intensity values, ordered like the wavlengths.
        cycle : int
            Measurement cycle number.
        spectype : str
            Measurement type ("on", "off", "static", "zero").
        csv_path : str, optional
            File path for saving. The default is "Spectrums.csv".

        Returns
        -------
        None.

        """
        if not os.path.isfile(csv_path):
            headers = ["timestamp", "cycle", "type"] + self.wavelengths.tolist()
            df_headers = pd.DataFrame([headers])
            df_headers.to_csv(csv_path, mode='w', header=False, index=False)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        spectrum_data = data.tolist()  # Convert NumPy array to list
        df = pd.DataFrame([[timestamp, cycle, spectype] + spectrum_data])
        df.to_csv(csv_path, mode='a', header=False, index=False)
