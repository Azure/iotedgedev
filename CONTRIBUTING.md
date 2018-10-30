Please fork, branch and pull-request any changes you'd like to make.

#### Contributor Dev Machine Setup

1. Clone this repository

    `git clone https://github.com/azure/iotedgedev.git`

1. Rename `.env.tmp` in the root of the repo to `.env` and set the `IOTHUB_CONNECTION_STRING` and `DEVICE_CONNECTION_STRING` values to settings from your IoT Hub and Edge Device. To set these values you could run `iotedgedev iothub setup` in the root of the repo.

1. Install **[Docker](https://docs.docker.com/engine/installation/)**
    - Windows    
        - Be sure to check whether you are running in Linux container mode or Windows container mode.
    - Linux
        - We've seen some issues with docker.io. If IoT Edge doesn't run for you, then try installing Docker CE directly instead of via docker.io. Use the [CE install steps](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce), or use the [convenience script](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-convenience-script).
        - By default, you need `sudo` to run `docker` commands. If you want to avoid this, please follow the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user).

1. Install **Python 2.7+**, **Python 3.6+**, and **pip**
    - Windows: [Install from Python's website](https://www.python.org/downloads/)
    - Linux: `sudo apt-get install python-pip python3-pip`
    - macOS: The OpenSSL used by the system built-in Python is old and vulnerable. Please use Python installed with [Homebrew](https://docs.brew.sh/Homebrew-and-Python).
    
1. Install **[Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)**

1. Install **[Azure CLI IoT extension](https://github.com/Azure/azure-iot-cli-extension/)**

    - New Install: `az extension add --name azure-cli-iot-ext`
    - Update Install: `az extension update --name azure-cli-iot-ext`

1. Install **[Node.js](https://nodejs.org/en/download/)** and the **`iothub-explorer`** package

    - `npm i -g iothub-explorer`

1. (Linux only) Install [Docker Compose](https://docs.docker.com/compose/)

    ```
    pip install -U docker-compose
    ```

1. (Linux only) Install extra system dependencies

    ```
    sudo apt-get install -y python2.7-dev libffi-dev libssl-dev
    ```

1. Install module dependencies
    ##### C# module and C# Azure Functions module
    Install **[.NET Core SDK 2.1 or later](https://www.microsoft.com/net/download)**

    ##### Python module
    1. Install **[Git](https://git-scm.com/)**
    2. Install **[Cookiecutter](https://github.com/audreyr/cookiecutter)**
    ```
    pip install -U cookiecutter
    ```

    ##### Node.js module
    1. Install **[Node.js](https://nodejs.org/en/download/)**
    2. Install **[Yeoman](http://yeoman.io/)** and **[Azure IoT Edge Node.js module generator](https://github.com/Azure/generator-azure-iot-edge-module)** packages
    ```
    npm i -g yo generator-azure-iot-edge-module
    ```

    ##### Java module
    1. Install **[JDK](https://www.oracle.com/technetwork/java/javase/downloads/index.html)**
    1. Install **[Maven](https://maven.apache.org/)**

1. Install Python development dependencies

    ```
    pip install -r requirements_dev.txt
    ```

1. Run IoT Edge Dev Tool in editable mode

    Run the following command from the root of the repo to see changes to iotedgedev commands as you change code.

    ```
    pip install -e .
    ```
 
#### VS Code Debugging
VS Code Debugging works only with Python 3.6 VS Code Python Environments for now. Make sure that your VS Code Python Environment is [pointing to Python 3.6](https://code.visualstudio.com/docs/python/environments#_how-to-choose-an-environment)

Set your CLI arguments in .vscode/launch.json and hit **F5**
 
#### Run Tests

Run the following command to run tests.
    
`tox`