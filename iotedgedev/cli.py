# -*- coding: utf-8 -*-

"""Console script for iotedgedev."""
from __future__ import absolute_import

import click
import sys
from .iotedgedev import Docker
from .iotedgedev import Modules
from .iotedgedev import Runtime
from .iotedgedev import Project
from .iotedgedev import Utility
from .iotedgedev import EnvVars
from .iotedgedev import Output

output = Output()
envvars = EnvVars(output)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option()
@click.option(
    '--set-config',
    default=False,
    required=False,
    is_flag=True,
    help="Expands Environment Variables in /config/*.json and copies to /build/config.")
def main(set_config):
    if(set_config):
        utility = Utility(envvars, output)
        utility.set_config()
    else:
        ctx = click.get_current_context()
        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())
            sys.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--create',
    default=".",
    required=False,
    help="Creates a new Azure IoT Edge project. Use `--create .` to create in current folder. Use `--create TEXT` to create in a subfolder.")
def project(create):
    if create:
        proj = Project(output)
        proj.create(create)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--build',
    default=False,
    required=False,
    is_flag=True,
    help="Builds and pushes modules specified in ACTIVE_MODULES Environment Variable to specified container registry.")
@click.option(
    '--deploy',
    default=False,
    required=False,
    is_flag=True,
    help="Deploys modules to Edge device using modules.json in build/config directory.")
def modules(build, deploy):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    mod = Modules(envvars, utility, output, dock)

    if build:
        mod.build()

    if deploy:
        mod.deploy()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--setup',
    default=False,
    required=False,
    is_flag=True,
    help="Setup Edge Runtime using runtime.json in build/config directory.")
@click.option(
    '--start',
    default=False,
    required=False,
    is_flag=True,
    help="Starts Edge Runtime. Calls iotedgectl start.")
@click.option(
    '--stop',
    default=False,
    required=False,
    is_flag=True,
    help="Stops Edge Runtime. Calls iotedgectl stop.")
@click.option(
    '--restart',
    default=False,
    required=False,
    is_flag=True,
    help="Restarts Edge Runtime. Calls iotedgectl stop, removes module containers and images, calls iotedgectl setup (with --config-file) and then calls iotedgectl start.")
@click.option(
    '--status',
    default=False,
    required=False,
    is_flag=True,
    help="Edge Runtime Status. Calls iotedgectl status.")
def runtime(setup, start, stop, restart, status):

    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    if setup:
        run.setup()

    if start:
        run.start()

    if stop:
        run.stop()

    if restart:
        run.restart()

    if status:
        run.status()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--setup-registry',
    default=False,
    required=False,
    is_flag=True,
    help="Pulls Edge Runtime from Docker Hub and pushes to your specified container registry. Also, updates config files to use CONTAINER_REGISTRY_* instead of the Microsoft Docker hub. See CONTAINER_REGISTRY Environment Variables.")
@click.option(
    '--clean',
    default=False,
    required=False,
    is_flag=True,
    help="Removes all the Docker containers and Images.")
@click.option(
    '--remove-modules',
    default=False,
    required=False,
    is_flag=True,
    help="Removes only the edge modules Docker containers and images specified in ACTIVE_MODULES, not edgeAgent or edgeHub.")
@click.option(
    '--remove-containers',
    default=False,
    required=False,
    is_flag=True,
    help="Removes all the Docker containers")
@click.option('--remove-images', default=False, required=False,
              is_flag=True, help="Removes all the Docker images.")
@click.option(
    '--logs',
    default=False,
    required=False,
    is_flag=True,
    help="Opens a new terminal window for edgeAgent, edgeHub and each edge module and saves to LOGS_PATH. You can configure the terminal command with LOGS_CMD.")
@click.option(
    '--show-logs',
    default=False,
    required=False,
    is_flag=True,
    help="Opens a new terminal window for edgeAgent, edgeHub and each edge module. You can configure the terminal command with LOGS_CMD.")
@click.option(
    '--save-logs',
    default=False,
    required=False,
    is_flag=True,
    help="Saves edgeAgent, edgeHub and each edge module logs to LOGS_PATH.")
def docker(
        setup_registry,
        clean,
        remove_modules,
        remove_containers,
        remove_images,
        logs,
        show_logs,
        save_logs):

    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)

    if setup_registry:
        dock.setup_registry()

    if clean:
        remove_containers = True
        remove_images = True

    if remove_modules:
        dock.remove_modules()

    if remove_containers:
        dock.remove_containers()

    if remove_images:
        dock.remove_images()

    if logs:
        show_logs = True
        save_logs = True

    if show_logs or save_logs:
        dock.handle_logs_cmd(show_logs, save_logs)


main.add_command(runtime)
main.add_command(modules)
main.add_command(docker)
main.add_command(project)


if __name__ == "__main__":
    main()
