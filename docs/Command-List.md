## Commands
**iotedgedev**
```
Usage: iotedgedev [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  add        Add a new module to the solution
  build      Build the solution
  deploy     Deploy solution to IoT Edge device
  genconfig  Expand environment variables and placeholders in deployment
             manifest template file and copy to config folder
  init       Create a new IoT Edge solution and provision Azure resources
  log        Open a new terminal window for EdgeAgent, EdgeHub and each Edge
             module and save to LOGS_PATH
  monitor    Monitor messages from IoT Edge device to IoT Hub
  new        Create a new IoT Edge solution
  push       Push module images to container registry
  setup      Setup IoT Edge simulator. This must be done before starting
  start      Start IoT Edge simulator
  stop       Stop IoT Edge simulator
  docker     Manage Docker
  iothub     Manage IoT Hub and IoT Edge devices
  simulator  Manage IoT Edge simulator
  solution   Manage IoT Edge solutions
```
**iotedgedev add**
```
Usage: iotedgedev add [OPTIONS] NAME

  Add a new module to the solution, where NAME is the module name

Options:
  -t, --template [c|csharp|java|nodejs|python|csharpfunction]
                                  Specify the template used to create the
                                  default module  [default: csharp]
  -g, --group-id TEXT             (Java modules only) Specify the groupId
                                  [default: com.edgemodule]
  -h, --help                      Show this message and exit.
```
**iotedgedev build**
```
Usage: iotedgedev build [OPTIONS]

  Build the solution

Options:
  -p, --push           Push module images to container registry  [default:
                       False]
  -d, --deploy         Deploy modules to Edge device using deployment.json in
                       the config folder  [default: False]
  -f, --file TEXT      Specify the deployment manifest template file
                       [default: deployment.template.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -h, --help           Show this message and exit.
```
**iotedgedev deploy**
```
Usage: iotedgedev deploy [OPTIONS]

  Deploy solution to IoT Edge device

Options:
  -f, --file TEXT  Specify the deployment manifest file  [default:
                   config\deployment.amd64.json]
  -h, --help       Show this message and exit.
```
**iotedgedev genconfig**
```
Usage: iotedgedev genconfig [OPTIONS]

  Expand environment variables and placeholders in deployment manifest
  template file and copy to config folder

Options:
  -f, --file TEXT      Specify the deployment manifest template file
                       [default: deployment.template.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -h, --help           Show this message and exit.
```
**iotedgedev init**
```
Usage: iotedgedev init [OPTIONS]

  Create a new IoT Edge solution and provision Azure resources

Options:
  -m, --module TEXT               Specify the name of the default module
                                  [default: filtermodule]
  -t, --template [c|csharp|java|nodejs|python|csharpfunction]
                                  Specify the template used to create the
                                  default module  [default: csharp]
  -g, --group-id TEXT             (Java modules only) Specify the groupId
                                  [default: com.edgemodule]
  -h, --help                      Show this message and exit.
```
**iotedgedev log**
```
Usage: iotedgedev log [OPTIONS]

  Open a new terminal window for EdgeAgent, EdgeHub and each Edge module and
  save to LOGS_PATH. You can configure the terminal command with LOGS_CMD.

Options:
  -l, --show  Open a new terminal window for EdgeAgent, EdgeHub and each Edge
              module. You can configure the terminal command with LOGS_CMD.
              [default: False]
  -s, --save  Save EdgeAgent, EdgeHub and each Edge module logs to LOGS_PATH.
              [default: False]
  -h, --help  Show this message and exit.
```
**iotedgedev monitor**
```
Usage: iotedgedev monitor [OPTIONS]

  Monitor messages from IoT Edge device to IoT Hub

Options:
  -t, --timeout TEXT  Specify number of seconds to monitor for messages
  -h, --help          Show this message and exit.
```
**iotedgedev new**
```
Usage: iotedgedev new [OPTIONS] NAME

  Create a new IoT Edge solution, where NAME is the solution folder name.
  Use "." as NAME to create in the current folder.

Options:
  -m, --module TEXT               Specify the name of the default module
                                  [default: filtermodule]
  -t, --template [c|csharp|java|nodejs|python|csharpfunction]
                                  Specify the template used to create the
                                  default module  [default: csharp]
  -g, --group-id TEXT             (Java modules only) Specify the groupId
                                  [default: com.edgemodule]
  -h, --help                      Show this message and exit.
```
**iotedgedev push**
```
Usage: iotedgedev push [OPTIONS]

  Push module images to container registry

Options:
  -d, --deploy         Deploy modules to Edge device using deployment.json in
                       the config folder  [default: False]
  --no-build           Inform the push command to not build module images
                       before pushing to container registry  [default: False]
  -f, --file TEXT      Specify the deployment manifest template file
                       [default: deployment.template.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -h, --help           Show this message and exit.
```
**iotedgedev setup**
```
Usage: iotedgedev setup [OPTIONS]

  Setup IoT Edge simulator. This must be done before starting

Options:
  -g, --gateway-host TEXT  GatewayHostName value for the module to connect.
                           [default: <your hostname>]
  -h, --help               Show this message and exit.
```
**iotedgedev start**
```
Usage: iotedgedev start [OPTIONS]

  Start IoT Edge simulator. To start in solution mode, use `iotedgdev
  simulator start -s [-v] [-b]`. To start in single module mode, use
  `iotedgedev simulator start -i input1,input2 [-p 53000]`

Options:
  -u, --setup          Setup IoT Edge simulator before starting.  [default:
                       False]
  -s, --solution       Start IoT Edge simulator in solution mode using the
                       deployment.json in config folder.  [default: False]
  -v, --verbose        Show the solution container logs.  [default: False]
  -b, --build          Build the solution before starting IoT Edge simulator
                       in solution mode.  [default: False]
  -f, --file TEXT      Specify the deployment manifest file. When `--build`
                       flag is set, specify a deployment manifest template and
                       it will be built.  [default:
                       config\deployment.amd64.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -i, --inputs TEXT    Start IoT Edge simulator in single module mode using
                       the specified comma-separated inputs of the target
                       module, e.g., `input1,input2`.
  -p, --port INTEGER   Port of the service for sending message.  [default:
                       53000]
  -h, --help           Show this message and exit.
```
**iotedgedev stop**
```
Usage: iotedgedev stop [OPTIONS]

  Stop IoT Edge simulator

Options:
  -h, --help  Show this message and exit.
```
**iotedgedev docker**
```
Usage: iotedgedev docker [OPTIONS] COMMAND [ARGS]...

  Manage Docker

Options:
  -h, --help  Show this message and exit.

Commands:
  clean  Remove all the containers and images
  log    Open a new terminal window for EdgeAgent, EdgeHub and each Edge
         module and save to LOGS_PATH
  setup  Pull Edge runtime images from MCR and push to your specified
         container registry
```
**iotedgedev docker clean**
```
Usage: iotedgedev docker clean [OPTIONS]

  Remove all the containers and images

Options:
  -m, --module     Remove only the Edge module containers and images, not
                   EdgeAgent or EdgeHub  [default: False]
  -c, --container  Remove all the containers  [default: False]
  -i, --image      Remove all the images  [default: False]
  -h, --help       Show this message and exit.
```
**iotedgedev docker log**
```
Usage: iotedgedev docker log [OPTIONS]

  Open a new terminal window for EdgeAgent, EdgeHub and each Edge module and
  save to LOGS_PATH. You can configure the terminal command with LOGS_CMD.

Options:
  -l, --show  Open a new terminal window for EdgeAgent, EdgeHub and each Edge
              module. You can configure the terminal command with LOGS_CMD.
              [default: False]
  -s, --save  Save EdgeAgent, EdgeHub and each Edge module logs to LOGS_PATH.
              [default: False]
  -h, --help  Show this message and exit.
```
**iotedgedev docker setup**
```
Usage: iotedgedev docker setup [OPTIONS]

  Pull Edge runtime images from Microsoft Container Registry and push to
  your specified container registry. Also, update config files to use
  CONTAINER_REGISTRY_* instead of the Microsoft Container Registry. See
  CONTAINER_REGISTRY environment variables.

Options:
  -h, --help  Show this message and exit.
```
**iotedgedev iothub**
```
Usage: iotedgedev iothub [OPTIONS] COMMAND [ARGS]...

  Manage IoT Hub and IoT Edge devices

Options:
  -h, --help  Show this message and exit.

Commands:
  monitor  Monitor messages from IoT Edge device to IoT Hub
  setup    Retrieve or create required Azure resources
```
**iotedgedev iothub monitor**
```
Usage: iotedgedev iothub monitor [OPTIONS]

  Monitor messages from IoT Edge device to IoT Hub

Options:
  -t, --timeout TEXT  Specify number of seconds to monitor for messages
  -h, --help          Show this message and exit.
```
**iotedgedev iothub setup**
```
Usage: iotedgedev iothub setup [OPTIONS]

  Retrieve or create required Azure resources

Options:
  --credentials <TEXT TEXT>...    Enter Azure Credentials (username password).
  --service-principal <TEXT TEXT TEXT>...
                                  Enter Azure Service Principal Credentials
                                  (username password tenant).
  --subscription TEXT             The Azure Subscription Name or Id.
                                  [required]
  --resource-group-location [australiaeast|australiasoutheast|brazilsouth|canadacentral|canadaeast|centralindia|centralus|eastasia|eastus|eastus2|japanwest|japaneast|northeurope|northcentralus|southindia|uksouth|ukwest|westus|westeurope|southcentralus|westcentralus|westus2]
                                  The Resource Group Location.  [required]
  --resource-group-name TEXT      The Resource Group Name (Creates a new
                                  Resource Group if not found).  [required]
  --iothub-sku [F1|S1|S2|S3]      The IoT Hub SKU.  [required]
  --iothub-name TEXT              The IoT Hub Name (Creates a new IoT Hub if
                                  not found).  [required]
  --edge-device-id TEXT           The IoT Edge Device Id (Creates a new Edge
                                  Device if not found).  [required]
  -u, --update-dotenv             If True, the current .env will be updated
                                  with the IoT Hub and Device connection
                                  strings.  [default: False; required]
  -h, --help                      Show this message and exit.
```
**iotedgedev simulator**
```
Usage: iotedgedev simulator [OPTIONS] COMMAND [ARGS]...

  Manage IoT Edge simulator

Options:
  -h, --help  Show this message and exit.

Commands:
  modulecred  Get the credentials of target module such as connection string
              and certificate file path.
  setup       Setup IoT Edge simulator. This must be done before starting
  start       Start IoT Edge simulator
  stop        Stop IoT Edge simulator
```
**iotedgedev simulator modulecred**
```
Usage: iotedgedev simulator modulecred [OPTIONS]

  Get the credentials of target module such as connection string and
  certificate file path.

Options:
  -l, --local             Set `localhost` to `GatewayHostName` for module to
                          run on host natively.  [default: False]
  -o, --output-file TEXT  Specify the output file to save the credentials. If
                          the file exists, its content will be overwritten.
  -h, --help              Show this message and exit.
```
**iotedgedev simulator setup**
```
Usage: iotedgedev simulator setup [OPTIONS]

  Setup IoT Edge simulator. This must be done before starting

Options:
  -g, --gateway-host TEXT  GatewayHostName value for the module to connect.
                           [default: <your hostname>]
  -h, --help               Show this message and exit.
```
**iotedgedev simulator start**
```
Usage: iotedgedev simulator start [OPTIONS]

  Start IoT Edge simulator. To start in solution mode, use `iotedgdev
  simulator start -s [-v] [-b]`. To start in single module mode, use
  `iotedgedev simulator start -i input1,input2 [-p 53000]`

Options:
  -u, --setup          Setup IoT Edge simulator before starting.  [default:
                       False]
  -s, --solution       Start IoT Edge simulator in solution mode using the
                       deployment.json in config folder.  [default: False]
  -v, --verbose        Show the solution container logs.  [default: False]
  -b, --build          Build the solution before starting IoT Edge simulator
                       in solution mode.  [default: False]
  -f, --file TEXT      Specify the deployment manifest file. When `--build`
                       flag is set, specify a deployment manifest template and
                       it will be built.  [default:
                       config\deployment.amd64.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -i, --inputs TEXT    Start IoT Edge simulator in single module mode using
                       the specified comma-separated inputs of the target
                       module, e.g., `input1,input2`.
  -p, --port INTEGER   Port of the service for sending message.  [default:
                       53000]
  -h, --help           Show this message and exit.
```
**iotedgedev simulator stop**
```
Usage: iotedgedev simulator stop [OPTIONS]

  Stop IoT Edge simulator

Options:
  -h, --help  Show this message and exit.
```
**iotedgedev solution**
```
Usage: iotedgedev solution [OPTIONS] COMMAND [ARGS]...

  Manage IoT Edge solutions

Options:
  -h, --help  Show this message and exit.

Commands:
  add        Add a new module to the solution
  build      Build the solution
  deploy     Deploy solution to IoT Edge device
  e2e        Push, deploy, start, monitor
  genconfig  Expand environment variables and placeholders in deployment
             manifest template file and copy to config folder
  init       Create a new IoT Edge solution and provision Azure resources
  new        Create a new IoT Edge solution
  push       Push module images to container registry
```
**iotedgedev solution add**
```
Usage: iotedgedev solution add [OPTIONS] NAME

  Add a new module to the solution, where NAME is the module name

Options:
  -t, --template [c|csharp|java|nodejs|python|csharpfunction]
                                  Specify the template used to create the
                                  default module  [default: csharp]
  -g, --group-id TEXT             (Java modules only) Specify the groupId
                                  [default: com.edgemodule]
  -h, --help                      Show this message and exit.
```
**iotedgedev solution build**
```
Usage: iotedgedev solution build [OPTIONS]

  Build the solution

Options:
  -p, --push           Push module images to container registry  [default:
                       False]
  -d, --deploy         Deploy modules to Edge device using deployment.json in
                       the config folder  [default: False]
  -f, --file TEXT      Specify the deployment manifest template file
                       [default: deployment.template.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -h, --help           Show this message and exit.
```
**iotedgedev solution build**
```
Usage: iotedgedev solution build [OPTIONS]

  Build the solution

Options:
  -p, --push           Push module images to container registry  [default:
                       False]
  -d, --deploy         Deploy modules to Edge device using deployment.json in
                       the config folder  [default: False]
  -f, --file TEXT      Specify the deployment manifest template file
                       [default: deployment.template.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -h, --help           Show this message and exit.
```
**iotedgedev solution deploy**
```
Usage: iotedgedev solution deploy [OPTIONS]

  Deploy solution to IoT Edge device

Options:
  -f, --file TEXT  Specify the deployment manifest file  [default:
                   config\deployment.amd64.json]
  -h, --help       Show this message and exit.
```
**iotedgedev solution e2e**
```
Usage: iotedgedev solution e2e [OPTIONS]

  Push, deploy, start, monitor

Options:
  -h, --help  Show this message and exit.
```
**iotedgedev solution genconfig**
```
Usage: iotedgedev solution genconfig [OPTIONS]

  Expand environment variables and placeholders in deployment manifest
  template file and copy to config folder

Options:
  -f, --file TEXT      Specify the deployment manifest template file
                       [default: deployment.template.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -h, --help           Show this message and exit.
```
**iotedgedev solution init**
```
Usage: iotedgedev solution init [OPTIONS]

  Create a new IoT Edge solution and provision Azure resources

Options:
  -m, --module TEXT               Specify the name of the default module
                                  [default: filtermodule]
  -t, --template [c|csharp|java|nodejs|python|csharpfunction]
                                  Specify the template used to create the
                                  default module  [default: csharp]
  -g, --group-id TEXT             (Java modules only) Specify the groupId
                                  [default: com.edgemodule]
  -h, --help                      Show this message and exit.
```
**iotedgedev solution new**
```
Usage: iotedgedev solution new [OPTIONS] NAME

  Create a new IoT Edge solution, where NAME is the solution folder name.
  Use "." as NAME to create in the current folder.

Options:
  -m, --module TEXT               Specify the name of the default module
                                  [default: filtermodule]
  -t, --template [c|csharp|java|nodejs|python|csharpfunction]
                                  Specify the template used to create the
                                  default module  [default: csharp]
  -g, --group-id TEXT             (Java modules only) Specify the groupId
                                  [default: com.edgemodule]
  -h, --help                      Show this message and exit.
```
**iotedgedev solution push**
```
Usage: iotedgedev solution push [OPTIONS]

  Push module images to container registry

Options:
  -d, --deploy         Deploy modules to Edge device using deployment.json in
                       the config folder  [default: False]
  --no-build           Inform the push command to not build module images
                       before pushing to container registry  [default: False]
  -f, --file TEXT      Specify the deployment manifest template file
                       [default: deployment.template.json]
  -P, --platform TEXT  Specify the platform  [default: amd64]
  -h, --help           Show this message and exit.
```
