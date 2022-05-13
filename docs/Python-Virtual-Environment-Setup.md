You can run IoT Edge Dev Tool inside a [Python Virtual Environment](https://docs.python.org/3/tutorial/venv.html). A Python virtual environment is a self-contained directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages.

1. Install `virtualenv`

    `pip install virtualenv`

2. Create a virtual environment

    `virtualenv venv`

    > `venv` is just a env name that can be anything you want, but we recommend sticking with `venv` if you want to contribute to IoT Edge Dev Tool because the `.gitignore` file excludes it.

    > To create a virtual environment with a Python version different with your system default, just use the `--python/-p` option to specify the Python executable path, *e.g.*:
    >
    > `virtualenv --python /usr/bin/python2.7 py27`

3. Activate the virtual environment

    - Windows
        - cmd.exe: `venv\Scripts\activate.bat`
        - PowerShell: `venv\Scripts\activate.ps1` (You may need to run `Set-ExecutionPolicy RemoteSigned` in an Administrator Powershell first to allow scripts to run)

    - Posix: `source venv/bin/activate`
    > It will be active until you deactivate it or close the terminal instance.

4. Install dependencies

    Continue with the instructions above starting with the [Manual Dev Machine Setup](Environment-Setup/Manual-Dev-Machine-Setup) -> Install Dependencies.

5. Deactivate the virtual environment

    When you are done with your virtualenv, you can deactivate it with the follow command:

    `deactivate`
