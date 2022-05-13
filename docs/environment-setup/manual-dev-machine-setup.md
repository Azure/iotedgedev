Here is what you need to do to get Azure IoT Edge Dev Tool (aka `iotedgedev`) running on your dev machine manually instead of using the IoT Edge Dev Container.

If you are using a separate Edge device, like a Raspberry Pi, you do not need to run all of these steps on your IoT Edge device, you can install and setup Edge runtime directly on the device. See the [Edge Device Setup](edge-device-setup) wiki page for more information on setting up your Edge device.

> Note: See the ["Test Coverage"](test-coverage) wiki page to see what the IoT Edge Dev Tool has been tested with.

1. Install **Python 2.7+ or Python 3.6+** and **pip** (Python 3.6 is recommended)
    - Windows: [Install from Python's website](https://www.python.org/downloads/)
    - Linux: `sudo apt install python-pip` or `sudo apt install python3-pip`
    - macOS: The OpenSSL used by the system built-in Python is old and vulnerable. Please use Python installed with [Homebrew](https://docs.brew.sh/Homebrew-and-Python)

2. Install **[Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)**

3. Install **[Azure CLI IoT extension](https://github.com/Azure/azure-iot-cli-extension/)**

    - New Install: `az extension add --name azure-iot`
    - Update Install: `az extension update --name azure-iot`

4. (Python < 3.5 only) Install **[Node.js](https://nodejs.org/en/download/)** and the **`iothub-explorer`** package

    - uamqp, which is needed by Azure CLI IoT extension for monitoring messages, is not supported in Python < 3.5. For Python < 3.5 users, please install [Node.js](https://nodejs.org/en/download/) and the `iothub-explorer` Node.js package: `npm i -g iothub-explorer`

5. (Raspberry Pi only) Install extra system dependencies

    ```sh
    sudo apt-get install python2.7-dev libffi-dev libssl-dev -y
    ```

6. (Linux only) Install [Docker Compose](https://docs.docker.com/compose/)

    ```sh
    pip install -U docker-compose
    ```

7. Install **`iotedgedev`**

    > You do not need to do this if you're going to be developing on iotedgedev

    > You do not need to run this on the Edge device. See the [Edge Device Setup](edge-device-setup) page for more information on setting up your Edge device.

    > You can also run under a Python Virtual Environment.  See the [Python Virtual Environment Setup](python-virtual-environment-setup) instructions page for details on how to set that up.

    > There is a known dependency conflict between `iotedgedev` and now-deprecated `azure-iot-edge-runtime-ctl`. Please make sure you have uninstalled `azure-iot-edge-runtime-ctl` before installing `iotedgedev`: `pip uninstall azure-iot-edge-runtime-ctl`, or use a clean virtual environment.

    ```sh
    pip install -U iotedgedev
    ```

8. Install module dependencies

    - **C# module and C# Azure Functions module**

        Install **[.NET Core SDK 2.1 or later](https://www.microsoft.com/net/download)**
        > You need .NET Core SDK 2.1 or later to run it on ARM. There is no official document on installing .NET Core SDK on ARM yet, but you can follow the [ARM32v7 Dockerfile](https://github.com/dotnet/dotnet-docker/blob/master/src/sdk/3.1/buster/arm32v7/Dockerfile).

    - **Python module**

      1. Install **[Git](https://git-scm.com/)**
      2. Install **[Cookiecutter](https://github.com/audreyr/cookiecutter)**

      ```sh
      pip install -U cookiecutter
      ```

    - **Node.js module**

      1. Install **[Node.js](https://nodejs.org/en/download/)**
      2. Install **[Yeoman](http://yeoman.io/)** and **[Azure IoT Edge Node.js module generator](https://github.com/Azure/generator-azure-iot-edge-module)** packages

      ```sh
      npm i -g yo generator-azure-iot-edge-module
      ```

    - **Java module**

      1. Install **[JDK](https://www.oracle.com/technetwork/java/javase/downloads/index.html)**
      2. Install **[Maven](https://maven.apache.org/)**

9. Follow the [Usage Wiki](usage) to learn the usage of IoT Edge Dev Tool
