# Contributing

This section describes how to get your developer workspace running for the first time so that you're ready to start making contributions.

Please fork, branch and pull-request any changes you'd like to make. For more information on how to create a fork, see: [Fork a repo - GitHub Docs](https://docs.github.com/en/get-started/quickstart/fork-a-repo)

## Workspace setup

1. Clone your fork of the repository

    `git clone https://github.com/<your_id>/iotedgedev.git`

1. Install **[Docker](https://docs.docker.com/engine/installation/)**
    - Windows
        - Be sure to check whether you are running in Linux container mode or Windows container mode.
    - Linux
        - We've seen some issues with docker.io. If IoT Edge doesn't run for you, then try installing Docker CE directly instead of via docker.io. Use the [CE install steps](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce), or use the [convenience script](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-convenience-script).
        - By default, you need `sudo` to run `docker` commands. If you want to avoid this, please follow the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user).

1. Setup development environment

    There are two options to setup your development environment:

    - **(Recommended)** Starting the devcontainer in VS Code (see [Developing inside a Container](https://code.visualstudio.com/docs/remote/containers) for steps on how to do so).
    - Setup the development environment manually. Please follow the [Manual Development Machine Setup Wiki](docs/environment-setup/manual-dev-machine-setup.md).
      - Run IoT Edge Dev Tool in editable mode

        Run the following command from the root of the repo to see changes to iotedgedev commands as you change code.

        ```sh
        pip install -e .
        ```

1. Rename `.env.tmp` in the root of the repo to `.env` and set the `IOTHUB_CONNECTION_STRING` and `DEVICE_CONNECTION_STRING` values to settings from your existing IoT Hub and Edge Device. If you don't have these, or want to create new ones, you could run `iotedgedev iothub setup` in the root of the repo to setup your resources and fill out the values automatically.

> NOTE: It is also possible to use [GitHub Codespaces](https://github.com/features/codespaces): after creating the Codespaces on your fork, all the above steps apply.

## Run and debug tests

To **run** and **debug** the tests **individually** you can use the VSCode Test Runner UI provided by the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (installed by default in the devcontainer).

An alternative way to **debug** is to select `Python: debug test file` in the `Run and debug` tab of vscode, open the test file you'd like to debug and hit `F5`.

You can choose one of these following commands to easily **run all** tests:

```sh
# Run all tests with all python interpreters (fails for the ones not installed)
# This is the command that runs in the pipeline for all python versions
make test-all
# Run tests with tox in python version 3.9 (the python version installed in the devcontainer)
tox -e py39
# Run all tests with pytest for python version 3.9 (nicest output, fastest)
make test
```

> It is recommended to run all tests with `tox -e py39` or `make test-all` at least once before making the PR. The pytest test runner environment is slightly different from tox, so some tests may pass with that and not in tox, resulting in failures in the pipeline.
