#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `iotedgedev` package."""


import unittest
import os
import shutil
from click.testing import CliRunner

from iotedgedev import iotedgedev
from iotedgedev import cli

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

project = "test_project"
root_dir = os.getcwd()

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
            
        except Exception as e:
            print(e)

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

    def test_version(self):
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

    # TODO: Figure out why tox messes with the paths.
    #def test_runtime_setup(self):
    #     runner = CliRunner()
    #     result = runner.invoke(cli.main, ['runtime', '--setup'])
    #     print(result.output)
    #     assert result.exit_code == 0
    #     assert 'Runtime setup successfully.' in result.output

    def test_docker_logs(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['docker', '--save-logs'])
        print(result.output)
        assert result.exit_code == 0
        assert 'Log files successfully saved' in result.output
    