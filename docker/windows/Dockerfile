FROM microsoft/windowsservercore:1709 AS base

SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

ENV PYTHON_VERSION 3.6.5
ENV NODEJS_VERSION 8.11.1
ENV DOTNETCORESDK_VERSION 2.1.4
ENV DESTINATION_FOLDER C:\\tools

WORKDIR /tmp

RUN $python_url = ('https://www.python.org/ftp/python/{0}/python-{0}.exe' -f $env:PYTHON_VERSION); \
    Write-Host ('Downloading {0}...' -f $python_url); \
    (New-Object System.Net.WebClient).DownloadFile($python_url, '/tmp/python-installer.exe'); \
    $install_folder = Join-Path -Path $env:DESTINATION_FOLDER -ChildPath 'python'; \
    Write-Host ('Installing into {0}...' -f $install_folder); \
    Start-Process python-installer.exe -Wait -ArgumentList @('/quiet', 'InstallAllUsers=1', 'TargetDir={0}' -f $install_folder, 'PrependPath=1', 'Shortcuts=0', 'Include_doc=0','Include_pip=1', 'Include_test=0'); 

RUN $node_url = ('https://nodejs.org/dist/v{0}/node-v{0}-x64.msi' -f $env:NODEJS_VERSION); \
    Write-Host ('Downloading {0}...' -f $node_url); \
    (New-Object System.Net.WebClient).DownloadFile($node_url, '/tmp/nodejs-installer.msi'); \
    $install_folder = Join-Path -Path $env:DESTINATION_FOLDER -ChildPath 'node'; \
    Write-Host ('Installing into {0}...' -f $install_folder); \
    Start-Process nodejs-installer.msi -Wait -ArgumentList @('/quiet', '/q', 'InstallDir={0}' -f $install_folder); 

RUN Write-Host ('Downloading Azure CLI...'); \
    Invoke-WebRequest 'https://aka.ms/installazurecliwindows' -OutFile azure-cli-installer.msi; \
    # $install_folder = Join-Path -Path $env:DESTINATION_FOLDER -ChildPath 'azcli'; \
    Write-Host ('Installing...'); \
    Start-Process azure-cli-installer.msi -Wait -ArgumentList @('/quiet', '/q');     
# Start-Process azure-cli-installer.msi -Wait -ArgumentList @('/quiet', '/q', 'InstallDir={0}' -f $install_folder); # Seems that InstallDir is not used at all

RUN $dotnetcoresdk_url = ('https://dotnetcli.blob.core.windows.net/dotnet/Sdk/{0}/dotnet-sdk-{0}-win-x64.zip' -f $env:DOTNETCORESDK_VERSION); \
    Write-Host ('Downloading {0}...' -f $dotnetcoresdk_url); \
    (New-Object System.Net.WebClient).DownloadFile($dotnetcoresdk_url, '/tmp/dotnetcoresdk.zip'); \
    Write-Host ('Unpacking .NET Core SDK...'); \
    Expand-Archive dotnetcoresdk.zip -DestinationPath ..\\tools\\dotnet; 

FROM microsoft/nanoserver:1709

RUN mkdir c:\\tools 
RUN mkdir c:\\tools\\azure

COPY --from=base ["tools", "/tools"]
COPY --from=base ["/Program Files (x86)/Microsoft SDKs/Azure/", "/tools/azure"]

USER ContainerAdministrator 
RUN setx /M PATH "%PATH%;C:\\tools\\dotnet;C:\\tools\\node\\;C:\tools\\python\\;C:\\tools\\python\\Scripts\\;c:\\tools\\azure\\CLI2\\wbin"
USER ContainerUser

RUN npm -i -g iothub-explorer 

RUN az extension add --name azure-cli-iot-ext
