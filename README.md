# XChroma

<a name="readme-top"></a>
> Manage quantum yeild and photofatigue experiments


[![Documentation](https://img.shields.io/website?url=https://alex6crbt.github.io/XChroma/)](https://alex6crbt.github.io/XChroma/)

<br />
<div align="center">
    <a href="https://alex6crbt.github.io/XChroma/">
        <img src="XChroma/ui/static/Logo.png" width="150" height="auto">
    </a>

  <h3 align="center">XChroma - Manage quantum yeild and photofatigue experiments</h3>

  <p align="left">
    XChroma is a Python-based experiment control software designed to manage and automate optical experiments for measuring the quantum yield and photofatigue of photoswitchable proteins. <br /> It supports programmable experimental sequences, allowing users to define custom light protocols for photoactivation and switching cycles.
    <br />
    <br />
  <p align="center">
    <a href="https://alex6crbt.github.io/XChroma"><strong>Learn More »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Alex6Crbt/XChroma/tree/main/XChroma"><strong>Code »</strong></a>
    ·
    <a href="https://github.com/Alex6Crbt/XChroma/issues">Report a bug</a>
    ·
    <a href="https://github.com/Alex6Crbt/XChroma/issues">Ask for a feature</a>
  </p>
  </p>
</div>

## Features

- **Experiment Control:** Interfaces with hardware to measure absorbance properties.
- **Programmable Sequences:** Define and execute custom sequences to trigger photoswitchable proteins under various conditions.
- **Real-Time Data Acquisition:** Collect and process experimental data in real time.
- **Modular Design:** Easy to extend with additional experimental protocols and analysis routines.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Alex6Crbt/XChroma.git
    cd XChroma
    ```

2. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Launch the app:**
    ```bash
    python main.py
    ```

## Custom Sequences

The `sequence.py` file enables you to create and customize your own experimental sequences. For more details, refer to the [documentation](https://alex6crbt.github.io/XChroma).

You can modify the `SequenceWorker` class to fit your needs or use the prebuilt measurement sequence classes available.


## Screenshots

![XChroma App Screenshot](docs/sources/static/captui.png)

## Project Structure

```
.
├── README.md
├── Spectrums.csv
├── XChroma
│   ├── __init__.py
│   ├── app.py
│   ├── arduino_control.py
│   ├── data_spectro.py
│   ├── process.py
│   ├── sequence_control.py
│   └── ui
│       ├── MainWindow.ui
│       ├── fonts/
│       ├── icons/
│       └── static/
├── docs
│   ├── Makefile
│   ├── make.bat
│   └── source
│       ├── _static/
│       ├── _templates/
│       ├── code/
│       ├── conf.py
│       ├── examples/
│       ├── index.rst
│       ├── quickstart.rst
│       └── userguide.rst
├── main.py
├── requirements.txt
└── sequence.py

```


## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b my-feature`).
3. Make your changes and test them.
4. Open a pull request describing your changes.

For major changes, please open an issue first to discuss your ideas.


## Future Documentation

More in-depth user guides, API documentation, and tutorial videos will be added soon. Stay tuned for updates!
