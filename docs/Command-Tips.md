### Setup Container Registry

You can also use IoT Edge Dev Tool to host the IoT Edge runtime from your own Azure Container Registry or a local container registry. Set the `.env` values for your container registry and run the following command. It will pull all the IoT Edge containers from Microsoft Container Registry, tag them and push them to the container registry you have specified in `.env`. 

> Use 'sudo' for Linux/Raspberry Pi

```
iotedgedev docker setup-registry
```


### View Docker Logs

#### Show Logs
IoT Edge Dev Tool also includes a "Show Logs" command that will open a new command prompt for each module it finds in your IoT Edge config. Just run the following command:

> Note: I haven't figured out how to launch new SSH windows in a reliable way.  It's in the backlog.  For now, you must be on the desktop of the machine to run this command.

```
iotedgedev docker log --show
```

You can configure the logs command in the `.env` file with the `LOGS_CMD` setting.  The `.env` file provides two options, one for [ConEmu](https://conemu.github.io/) and one for Cmd.exe.

#### Save Logs

You can also output the logs to the LOGS_PATH directory.  The following command will output all the logs and add them to an `edge-logs.zip` file that you can send to the Azure IoT support team if they request it.

```
iotedgedev docker log --save
```

#### Both Show and Save Logs

Run the following to show and save logs with a single command

```
iotedgedev docker log --show --save
```


### Local Docker Registry Setup

Instead of using a cloud based container registry, you can use a local Docker registry. Here's how to get it setup.

1. Set `CONTAINER_REGISTRY_SERVER` in `.env` file to `localhost:5000`. You can enter a different port if you'd like to.
1. Add `localhost:5000` and `127.0.0.1:5000` to Docker -> Settings -> Daemon -> Insecure Registries

> In the latest IoT Edge Dev Tool, Step 2 above hasn't been required. But, if you run into issues, you may want to try adding those Insecure Registries.

IoT Edge Dev Tool will look for `localhost` in your setting and take care of the rest for you.