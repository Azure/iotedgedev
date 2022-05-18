IoT Edge Dev Tool 0.82.0 provides support for the GA release of Azure IoT Edge and other new features, while on the other hand, introduces some breaking changes to better serve these new features. If you have used IoT Edge Dev Tool during the Azure IoT Edge public preview, this document will help you migrate your code and workflow to IoT Edge Dev Tool 0.82.0.

## Retirement of `iotedgectl`
With the GA release of Azure IoT Edge, iotedgectl (a.k.a, [azure-iot-edge-runtime-ctl](https://pypi.org/project/azure-iot-edge-runtime-ctl/)) is retired. In IoT Edge Dev Tool 0.82.0, we replace `iotedgectl` with the IoT Edge Simulator provided by the [iotedgehubdev CLI](https://pypi.org/project/iotedgehubdev/). The `setup`, `start`, and `stop` commands will now control IoT Edge Simulator instead.

## Updated command list and options
IoT Edge Dev Tool 0.82.0 comes with a new CLI UX. All commands are organized into four categories: `docker`, `iothub`, `simulator`, and `solution`. The general style is **iotedgedev _category_ _command_ --_parameter_**. For some frequently used commands, there is also an **iotedgedev _command_ --_parameter_** style shortcut (only if the shortcut won't cause confusion, similar to the relationship between `docker logs` and `docker container logs`). The shortcuts also add backward compatibility with some public preview style commands.

Here is what you would see when you type `iotedgedev --help` (shortcuts are intentionally listed before the categories):

```
$ iotedgedev --help
Usage: iotedgedev [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  add        Add a new module to the solution
  build      Build the solution
  deploy     Deploy solution to IoT Edge device
  genconfig  Expand environment variables and placeholders in *.template.json
             and copy to config folder
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

Here is the help message for a category:

```
$ iotedgedev solution --help
Usage: iotedgedev solution [OPTIONS] COMMAND [ARGS]...

  Manage IoT Edge solutions

Options:
  -h, --help  Show this message and exit.

Commands:
  add        Add a new module to the solution
  build      Build the solution
  deploy     Deploy solution to IoT Edge device
  e2e        Push, deploy, start, monitor
  genconfig  Expand environment variables and placeholders in *.template.json
             and copy to config folder
  init       Create a new IoT Edge solution and provision Azure resources
  new        Create a new IoT Edge solution
  push       Push module images to container registry
```

Here is the help message for a specific command. Only the parameters relevant to the command are listed. In addition, parameter shortcuts are also added, like `-t` below for `--template`, whenever possible.

```
$ iotedgedev solution add --help
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

Below is a full table of the public preview commands, new commands, and shortcuts (if applicable):

| Public Preview Command                                                                                                                                                       | New Command                                                                                                                                                                    | Shortcut                         |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------- |
| `--set-config`                                                                                                                                                               | `solution genconfig`                                                                                                                                                           | `genconfig `                     |
| `solution --create --module --template`                                                                                                                                      | `solution new --module/-t --template/-t`                                                                                                                                       | `new`                            |
| `init`                                                                                                                                                                       | `solution init`                                                                                                                                                                | `init`                           |
| `e2e`                                                                                                                                                                        | `solution e2e`                                                                                                                                                                 |
| `addmodule --template`                                                                                                                                                       | `solution add --template/-t`                                                                                                                                                   | `add --template/-t`              |
| `build --push --deploy`                                                                                                                                                      | `solution build --push/-p --deploy/-d`                                                                                                                                         | `build --push/-p --deploy/-d`    |
| `push --deploy --no-build`                                                                                                                                                   | `solution push --deploy/-d --no-build`                                                                                                                                         | `push --deploy/-d --no-build`    |
| `deploy`                                                                                                                                                                     | `solution deploy`                                                                                                                                                              | `deploy`                         |
| `monitor --timeout`                                                                                                                                                          | `iothub monitor --timeout/-t`                                                                                                                                                  | `monitor --timeout/-t`           |
| `azure --setup --credentials --service-principal --subscription --resource-group-location --resource-group-name --iothub-sku --iothub-name --edge-device-id --update-dotenv` | `iothub setup --credentials --service-principal --subscription --resource-group-location --resource-group-name --iothub-sku --iothub-name --edge-device-id --update-dotenv/-u` |
| `modules --add --template`                                                                                                                                                   | `solution add --template`                                                                                                                                                      | `add --template/-t`              |
| `modules --build --push --deploy`                                                                                                                                            | `solution build --push/-p --deploy/-d`                                                                                                                                         | `build --push/-p --deploy/-d`    |
| `modules --push --deploy`                                                                                                                                                    | `solution push --deploy/-d --no-build`                                                                                                                                         | `push --deploy/-d --no-build`    |
| `modules --deploy`                                                                                                                                                           | `solution deploy`                                                                                                                                                              | `deploy`                         |
| `runtime --setup`                                                                                                                                                            | *deprecated, see [Retirement of `iotedgectl`](#retirement-of-iotedgectl) section*                                                                                              |
| `runtime --start`                                                                                                                                                            | *deprecated, see [Retirement of `iotedgectl`](#retirement-of-iotedgectl) section*                                                                                              |
| `runtime --stop`                                                                                                                                                             | *deprecated, see [Retirement of `iotedgectl`](#retirement-of-iotedgectl) section*                                                                                              |
| `runtime --restart`                                                                                                                                                          | *deprecated, see [Retirement of `iotedgectl`](#retirement-of-iotedgectl) section*                                                                                              |
| `runtime --status`                                                                                                                                                           | *deprecated, see [Retirement of `iotedgectl`](#retirement-of-iotedgectl) section*                                                                                              |
| `docker --setup-registry`                                                                                                                                                    | `docker setup`                                                                                                                                                                 |
| `docker --clean --remove-modules --remove-containers --remove-images`                                                                                                        | `docker clean --modules/-m --containers/-c --image/-i`                                                                                                                         |
| `docker --logs --show-logs --save-logs`                                                                                                                                      | `docker log --show/-l --save/-s`                                                                                                                                               | `docker log --show/-l --save/-s` |

### Deployment manifest template
IoT Edge Dev Tool 0.82.0 relies on the deployment manifest template to build the solution (see [Deprecation of `ACTIVE_MODULES`](#deprecation-of-active_modules) section for details). By default, it's the `deployment.template.json` file in the root of the solution folder, but you can also customize it with the `DEPLOYMENT_CONFIG_TEMPLATE_FILE` environment variable. The major difference between deployment manifest template and deployment manifest is that module image URLs in deployment manifest template can be placeholders (whose format looks like `${MODULES.filtermodule.amd64}`). The image placeholders can help you easily update the referenced module and image platform without typing lengthy image URLs. When building solutions, IoT Edge Dev Tool will parse the image placeholders, expand them with the actual image URLs and save the results in the deployment manifest in the config output folder. By default, it's the `deployment.json` file in the `config` folder, but you can also customize it with the `DEPLOYMENT_CONFIG_FILE` and `CONFIG_OUTPUT_DIR` environment variables. In addition, when adding modules, IoT Edge Dev Tool will add a corresponding section for the module in the deployment manifest template with `${MODULES.<module-name>.amd64}` as the image.

To migrate your solutions created in the public preview to leverage the new build process, you can rename your deployment manifest, and update the images of the modules which you want to build with the corresponding image placeholders.

### New module folder structure
IoT Edge Dev Tool now calls module templates when adding new modules to the solution. For C# module developers, you don't need to execute `dotnet new` commands yourself. You only need to execute `iotedgedev add` command, specify the module name and template (for example, `csharp` or `csharpfunction`). IoT Edge Dev Tool will scaffold a new module from the template, save the module files in the `${MODULES_PATH}/<module-name>` folder (`modules/<module-name>` by default), and update the deployment manifest template for you. In each module folder, there are now four types of files:
* Module code files, for example, `Program.cs` and `*.csproj`
* Dockerfiles for each platform, for example, `Dockerfile.amd64`, `Dockerfile.amd64.debug` and `Dockerfile.arm32v7`
* `module.json` file which specifies the meta-data of the module, including image repository, mapping between platforms and Dockerfiles, and build options.
* Miscellaneous files, for example, `.gitignore`.

To migrate your modules created in the public preview to work with IoT Edge Dev Tool 0.82.0, you need to create a module.json file from [here](https://github.com/Azure/dotnet-template-azure-iot-edge-module/blob/master/content/dotnet-template-azure-iot-edge-module/CSharp/module.json), update the `repository` as the module image repository such as `myregistry.azurecr.io/filtermodule`, or with environment variable placeholders `${CONTAINER_REGISTRY_SERVER}/filtermodule`. Next you need to update the `platforms` dictionary to make sure that platform-Dockerfile mapping is correct. The built module image will have the tag format `<repository>:<version>-<platform>`, for example `myregistry.azurecr.io/filtermodule:0.0.1-amd64`.

### Building code in Dockerfiles
The recent releases of IoT Edge module templates ship with Dockerfiles which will build the code binaries in the containers. For example, C# module developers now don't need to run `dotnet build` or `dotnet publish` on their development machine. A single `docker build` command will build the binaries in the container and copy them to the final module image. You can check the C# module template Dockerfile [here](https://github.com/Azure/dotnet-template-azure-iot-edge-module/blob/master/content/dotnet-template-azure-iot-edge-module/CSharp/Dockerfile.amd64), which leverages Docker's [multi-stage build feature](https://docs.docker.com/develop/develop-images/multistage-build/). On the other hand, IoT Edge Dev Tool is continuously adding support for modules in more languages such as Node.js and Python, with diverse steps to build. As a result, the `iotedgedev build` command will only build the Dockerfiles, but not run language-specific building commands.

### Deprecation of `ACTIVE_MODULES`
With the full support of deployment manifest template for module management, IoT Edge Dev Tool 0.82.0 now comes with new logic of determining which Dockerfiles to build. The `ACTIVE_MODULES` environment variable will be replaced by the image placeholders (whose format looks like `${MODULES.filtermodule.amd64}`) in deployment manifest template, and the `BYPASS_MODULES` and `ACTIVE_DOCKER_PLATFORMS` environment variables jointly. IoT Edge Dev Tool will built a Dockerfile if it meets either of the following two requirements:
1. The module name is not in `BYPASS_MODULES`, and a module specifies `${MODULES.<module-name>.<platform>}` as its image in the deployment manifest template.
1. The module name is not in `BYPASS_MODULES`, and the platform is in `ACTIVE_DOCKER_PLATFORMS`.

The default value of `BYPASS_MODULES` and `ACTIVE_DOCKER_PLATFORM` are both `""`, which means you only need to update the deployment manifest template to specify which Dockerfiles to build. Although this will serve most requirements, you are free to update `BYPASS_MODULES` and `ACTIVE_DOCKER_PLATFORM` for your specific scenarios.

### Misc
