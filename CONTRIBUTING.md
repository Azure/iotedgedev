Please fork, branch and pull-request any changes you'd like to make.

#### Contributor Dev Machine Setup

1. Clone or Fork this Repository

    `git clone https://github.com/azure/iotedgedev.git`

1. Rename `.env.tmp` in the root of the repo to `.env` and set the `IOTHUB_CONNECTION_STRING` and `DEVICE_CONNECTION_STRING` values to settings from your IoT Hub and Edge Device. To set these values you could run `iotedgedev iothub setup` in the root of the repo.

1. Follow the [Manual Setup Wiki](https://github.com/Azure/iotedgedev/wiki/manual-dev-machine-setup) to setup install dependencies for running iotedgedev.

1. Install development dependencies

    Run the following command to install all the dependencies needed to build iotedgedev and run the tests.

    ```
    pip install -r requirements_dev.txt
    ```

1. Editable Mode

    Run the following command from the root of the IoT Edge Dev Tool Solution to see changes to iotedgedev commands as you change code.

    ```
    pip install -e .
    ```
 
#### VS Code Debugging
VS Code Debugging works only with Python 3.6 VS Code Python Environments for now. Make sure that your VS Code Python Environment is [pointing to Python 3.6](https://code.visualstudio.com/docs/python/environments#_how-to-choose-an-environment)

Set your CLI arguments in launch.json and hit **F5**
 
#### Run Tests

Run the following command to run tests.
    
`tox`