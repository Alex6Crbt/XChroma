QuickStart
==========


Installation
------------


.. dropdown:: 1. **Prerequisites**   :octicon:`code`
    :animate: fade-in-slide-down

    Make sure Python 3.9 is installed on your system.
    If you haven't installed Python, you can download it from `the official Python website <https://www.python.org>`_.

.. dropdown:: 2. **Download the Project from GitHub** :octicon:`mark-github`
    :open:
    :animate: fade-in-slide-down

    You can get the project source code by cloning the GitHub repository or downloading it as a ZIP file.

    .. tab-set::

        .. tab-item:: Clone via Git

            .. code-block:: console

                git clone https://github.com/Alex6Crbt/XChroma.git
                cd XChroma

        .. tab-item:: Download ZIP

            1. Go to the github repo (https://github.com/Alex6Crbt/XChroma).
            2. Click the **Code** button and select **Download ZIP**.
            3. Extract the ZIP file and navigate to the project directory.

            .. code-block:: console

                cd XChroma

.. dropdown:: 3. **Create a Virtual Environment (Optional)** :octicon:`code`
    :animate: fade-in-slide-down

    It is recommended to create a virtual environment to isolate project dependencies.
    Open a terminal or command prompt and run the following commands:

    .. tab-set::

        .. tab-item:: On macOS and Linux:

            .. code-block:: console

                python3 -m venv myenv
                source myenv/bin/activate

        .. tab-item:: On Windows:

            .. code-block:: console

                python -m venv myenv
                myenv\Scripts\activate


.. dropdown:: 4. Install Required Packages :octicon:`download`
    :open:
    :animate: fade-in-slide-down

    In the virtual environment or your Python environment,
    run the following command to install the necessary packages:

    .. code-block:: console

        pip install -r requirements.txt


.. dropdown:: 5. **Launch the App** :octicon:`rocket`
    :open:
    :animate: fade-in-slide-down

    Before running the application, make sure to connect the required hardware:

    - **Ocean Spectrometer**: Ensure it is properly connected
    - **Arduino (if needed)**: If your setup includes an Arduino, connect it via USB and verify communication.

    Once all necessary devices are connected, in the project directory run the application:

    .. code-block:: console

        python main.py


.. tip::

    Now that you have installed all the necessary prerequisites and dependencies,
    feel free to check the library documentation for more information on
    usage and different algorithms.
