Reference
=========

The XChroma application is based on four different modules, each handling a specific aspect of the application.


Modules
-------

.. grid:: 2

    .. grid-item-card::  XChroma.app module
       :link: XChroma.app
       :link-type: doc

       The main application module that initializes and manages the graphical user interface (GUI) for XChroma.

    .. grid-item-card::  XChroma.arduino_control module
       :link: XChroma.arduino_control
       :link-type: doc

       Handles communication with the Arduino, allowing control of connected hardware components such as servos and sensors.

.. grid:: 2

    .. grid-item-card::  XChroma.data_spectro module
       :link: XChroma.data_spectro
       :link-type: doc

       Manages spectral data, including intensity measurements, absorbance calculations, and data preprocessing.

    .. grid-item-card::  XChroma.sequence_control module
       :link: XChroma.sequence_control
       :link-type: doc

       Implements sequence execution logic, managing automated workflows and data collection processes.


Module contents
---------------

.. automodule:: XChroma
   :members:
   :undoc-members:
   :show-inheritance:

.. toctree::
    :maxdepth: 2

    XChroma.app

    XChroma.arduino_control

    XChroma.data_spectro

    XChroma.sequence_control
