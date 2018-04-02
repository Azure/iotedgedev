FROM microsoft/windowsservercore:1709

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

ENV PYTHON_VERSION 3.6.5
ENV NODEJS_VERSION 8.11.1
ENV DOTNETCORESDK_VERSION 2.1.101

WORKDIR /tmp

RUN $python_url = ('https://www.python.org/ftp/python/{0}/python-{0}.exe' -f $env:PYTHON_VERSION); \
    Write-Host ('Downloading {0}...' -f $python_url); \
    (New-Object System.Net.WebClient).DownloadFile($python_url, '/tmp/python-installer.exe'); \
    Write-Host ('Installing Python...'); \
    Start-Process python-installer.exe -Wait -ArgumentList @('/quiet', 'InstallAllUsers=1', 'TargetDir=C:\Python3', 'PrependPath=1', 'Shortcuts=0', 'Include_doc=0','Include_pip=1', 'Include_test=0'); \
    $env:PATH = [Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::Machine);

RUN $node_url = ('https://nodejs.org/dist/v{0}/node-v{0}-x64.msi' -f $env:NODEJS_VERSION); \
    Write-Host ('Downloading {0}...' -f $node_url); \
    (New-Object System.Net.WebClient).DownloadFile($node_url, '/tmp/nodejs-installer.msi'); \
    Write-Host ('Installing Node...'); \
    Start-Process nodejs-installer.msi -Wait -ArgumentList @('/quiet', '/q'); \
    $env:PATH = [Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::Machine);

RUN Write-Host ('Downloading Azure CLI...'); \
    Invoke-WebRequest 'https://aka.ms/installazurecliwindows' -OutFile azure-cli-installer.msi; \
    Write-Host ('Installing Azure CLI...'); \
    Start-Process azure-cli-installer.msi -Wait -ArgumentList @('/quiet', '/q');  \
    $env:PATH = [Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::Machine);

RUN $dotnetcoresdk_url = ('https://download.microsoft.com/download/D/C/F/DCFA73BE-93CE-4DA0-AB76-98972FD6E475/dotnet-sdk-{0}-win-x64.exe' -f $env:DOTNETCORESDK_VERSION); \
    Write-Host ('Downloading {0}...' -f $dotnetcoresdk_url); \
    (New-Object System.Net.WebClient).DownloadFile($dotnetcoresdk_url, '/tmp/dotnetcoresdk-installer.exe'); \
    Write-Host ('Installing .NET Core SDK...'); \
    Start-Process dotnetcoresdk-installer.exe -Wait -ArgumentList @('/quiet'); \
    $env:PATH = [Environment]::GetEnvironmentVariable('PATH', [EnvironmentVariableTarget]::Machine);

RUN Write-Host ('Installing AZ CLI IOT Extension...'); \
    az extension add --name azure-cli-iot-ext

RUN Start-Process npm -Wait -ArgumentList @('i', '-g', 'iothub-explorer'); 

WORKDIR /iotedge

COPY install-dev.bat /scripts/install-dev.bat