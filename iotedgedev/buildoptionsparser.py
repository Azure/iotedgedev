import functools
import re

from .output import Output


def parse_to_dict(split_func, sdk_options, sdk_key, build_option_val):
    if sdk_key not in sdk_options:
        sdk_options[sdk_key] = {}
    k, v = split_func(build_option_val)
    sdk_options[sdk_key][k] = v


def parse_to_list(sdk_options, sdk_key, build_option_val):
    if sdk_key not in sdk_options:
        sdk_options[sdk_key] = []
    sdk_options[sdk_key].append(build_option_val)


def parse_val(sdk_options, sdk_key, build_option_val):
    sdk_options[sdk_key] = build_option_val


def parse_container_limits(sdk_options, sdk_key, build_option_val):
    if 'container_limits' not in sdk_options:
        sdk_options['container_limits'] = {}
    sdk_options['container_limits'][sdk_key] = build_option_val


def parse_flag(sdk_options, sdk_key, build_option_val):
    if not build_option_val:
        sdk_options[sdk_key] = True
    else:
        build_option_val = build_option_val.lower()
        if build_option_val == 'true':
            sdk_options[sdk_key] = True
        elif build_option_val == 'false':
            sdk_options[sdk_key] = False
        else:
            raise ValueError("Bool value should be 'True' or 'False'.")


def split_build_option(build_option_str):
    parsed_option = re.compile(r"\s+").split(build_option_str)
    if len(parsed_option) == 1:
        parsed_option = parsed_option[0].split('=', 1)
    if len(parsed_option) == 1:
        return parsed_option[0], None
    return parsed_option[0], parsed_option[1]


def split_host(host):
    if ':' in host:
        return host.split(':', 1)
    else:
        raise Exception('Error host:ip format.')


def split_arg(arg):
    if '=' in arg:
        return arg.split('=', 1)
    else:
        return arg, None


def split_kv(kvpair):
    if '=' in kvpair:
        return kvpair.split('=', 1)
    else:
        return kvpair, ''


# Mapping docker build cli command to docker python sdk.
# Format: cli_key : [sdk_key, parse_func]
# The commented items are cli build options not supported in python sdk.
cli_sdk_mapping = {
    '--add-host': ['extra_hosts', functools.partial(parse_to_dict, split_host)],
    '--build-arg': ['buildargs', functools.partial(parse_to_dict, split_arg)],
    '--cache-from': ['cache_from', parse_to_list],
    # '--cgroup-parent' : ['sdk_key', parse_func],
    # '--compress' : ['sdk_key', parse_func],
    # '--cpu-period' : ['sdk_key', parse_func],
    # '--cpu-quota' : ['sdk_key', parse_func],
    '--cpu-shares': ['cpushares', parse_container_limits],
    '-c': ['cpushares', parse_container_limits],
    '--cpuset-cpus': ['cpusetcpus', parse_container_limits],
    # '--cpuset-mems' : ['sdk_key', parse_func],
    # '--disable-content-trust' : ['sdk_key', parse_func],
    '--file': ['dockerfile', parse_val],
    '-f': ['dockerfile', parse_val],
    '--force-rm': ['forcerm', parse_flag],
    # '--iidfile' : ['sdk_key', parse_func],
    '--label': ['labels', functools.partial(parse_to_dict, split_kv)],
    '--memory': ['memory', parse_container_limits],
    '-m': ['memory', parse_container_limits],
    '--memory-swap': ['memswap', parse_container_limits],
    '--network': ['network_mode', parse_val],
    '--no-cache': ['nocache', parse_flag],
    '--platform': ['platform', parse_val],
    '--pull': ['pull', parse_flag],
    '--quiet': ['quiet', parse_flag],
    '-q': ['quiet', parse_flag],
    '--rm': ['rm', parse_flag],
    # '--security-opt' : ['sdk_key', parse_func],
    '--shm-size': ['shmsize', parse_val],
    '--squash': ['squash', parse_flag],
    # '--stream' : ['sdk_key', parse_func],
    '--tag': ['tag', parse_val],
    '-t': ['tag', parse_val],
    '--target': ['target', parse_val]
    # '--ulimit' : ['sdk_key', parse_func]
}

# Class BuildOptionsParser parses docker cli build commands to python sdk dict.


class BuildOptionsParser(object):
    filter_set = ["--rm", "--tag", "-t", "--file", "-f"]

    def __init__(self, build_options):
        self.build_options = build_options
        self.output = Output()
        self.sdk_options = {}

    def _filter_build_options(self):
        """Remove build options which will be ignored"""
        if self.build_options is None:
            return None

        filtered_build_options = []
        for build_option in self.build_options:
            build_option = build_option.strip()
            cli_key, cli_val = split_build_option(build_option)
            if cli_key:
                if cli_key not in BuildOptionsParser.filter_set:
                    filtered_build_options.append((cli_key, cli_val))
                else:
                    self.output.info('Build option {0} will be ignored.'.format(cli_key))

        return filtered_build_options

    def parse_build_options(self):
        """Parse build options to python SDK"""
        filtered_build_options = self._filter_build_options()
        for cli_key, cli_val in filtered_build_options:
            if cli_key not in cli_sdk_mapping:
                raise KeyError('Not supported build option {0}.'.format(cli_key))
            sdk_key = cli_sdk_mapping[cli_key][0]
            parse_func = cli_sdk_mapping[cli_key][1]
            parse_func(self.sdk_options, sdk_key, cli_val)
        return self.sdk_options
