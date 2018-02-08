#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `iotedgedev` package."""


import unittest
import os
import sys
import shutil
from click.testing import CliRunner

from iotedgedev import cli
from iotedgedev.azurecli import AzureCli

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

project = "test_project"
root_dir = os.getcwd()

class TestAzureCli(AzureCli):
    def invoke_az_cli(self, args, error_message=None, io=None):
        return True

class TestIotedgedev(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """SETUP"""
        print("SETTING UP TEST PROJECT")
        try:
            runner = CliRunner()
            result = runner.invoke(cli.main, ['project', '--create', project])
            #print(result.output)
            #assert result.exit_code == 0
            #assert 'Azure IoT Edge project created' in result.output

            shutil.copyfile('.env', os.path.join(os.getcwd(), project, '.env'))
            os.chdir(project)

        except Exception as ex:
            print(str(ex))

    @classmethod
    def tearDownClass(self):
        """TEARDOWN"""
        os.chdir("..")
        shutil.rmtree(os.path.join(root_dir, project), ignore_errors=True)

    def test_version(self):
        """VERSION"""
        runner = CliRunner()
        result = runner.invoke(cli.main, ['--version'])
        print(result.output)
        assert result.exit_code == 0
        assert 'version' in result.output

    def test_help(self):
        """HELP"""
        runner = CliRunner()
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert 'Show this message and exit.' in help_result.output

    def test_modules_build_deploy(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['modules', '--build'])
        print(result.output)
        assert result.exit_code == 0
        assert '0 Error(s)' in result.output
        result = runner.invoke(cli.main, ['modules', '--deploy'])
        print(result.output)
        assert result.exit_code == 0
        assert 'Edge Device configuration successfully deployed' in result.output

    def test_alternate_dotenv_file(self):
        dotenv_file = ".env.test"
        shutil.copyfile('../.env', dotenv_file)
        os.environ["DOTENV_FILE"] = dotenv_file

        runner = CliRunner()
        result = runner.invoke(cli.main, ['--set-config'])
        print(result.output)
        assert result.exit_code == 0
        test_string = "Environment Variables loaded from: " + dotenv_file
        assert test_string in result.output

    #TODO implement the mock AzureCli class
    '''
    def test_azure_setup_command(self):
        dotenv_file = ".env.test"
        shutil.copyfile('../.env', dotenv_file)
        os.environ["DOTENV_FILE"] = dotenv_file

        runner = CliRunner()
        result = runner.invoke(cli.main, [
                               'azure', '--setup',
                               '--credentials', 'username', 'password',
                               '--subscription', '12341234-1234-1234-1234-123412341234',
                               '--resource-group-name', 'iotedgedev-rg-dev',
                               '--iothub-name', 'iotedgedev-iothub-dev',
                               '--edge-device-id', 'iotedgedev-edgedevice-dev',
                               '--update-dotenv'
                               ], az_cli = TestAzureCli(sys.stdout) )
        print(result.output)
        assert result.exit_code == 0
        test_string = "Environment Variables loaded from: " + dotenv_file
        assert test_string in result.output
    '''
    # TODO: Figure out why tox messes with the paths.
    '''
    def test_runtime_setup(self):
         runner = CliRunner()
         result = runner.invoke(cli.main, ['runtime', '--setup'])
         print(result.output)
         assert result.exit_code == 0
         assert 'Runtime setup successfully.' in result.output

    def test_docker_logs(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['docker', '--save-logs'])
        print(result.output)
        assert result.exit_code == 0
        assert 'Log files successfully saved' in result.output
    '''

    # TODO: Figure out why tox doesn't work in this case. Manually test it for now.
    '''
    def test_no_dotenv_file(self):
        dotenv_file = ".env.nofile"
        os.environ["DOTENV_FILE"] = dotenv_file

        runner = CliRunner()
        result = runner.invoke(cli.main, ['--set-config'])
        print(result.output)
        assert result.exit_code == 0
        test_string = "{0} file not found on disk".format(dotenv_file)
        assert test_string in result.output
    '''

