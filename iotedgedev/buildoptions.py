import functools
import re


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
    sdk_options[sdk_key] = True


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
    '--cpuset-cpus	': ['cpusetcpus', parse_container_limits],
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
    '-q': ['quiet', parse_val],
    '--rm': ['rm', parse_flag],
    # '--security-opt' : ['sdk_key', parse_func],
    '--shm-size': ['shmsize', parse_val],
    '--squash': ['squash', parse_flag],
    # '--stream' : ['sdk_key', parse_func],
    '--tag': ['tag', parse_val],
    '-t': ['tag', parse_val],
    '--target': ['target', parse_val],
    # '--ulimit' : ['sdk_key', parse_func]
}


def parse_build_options(build_options):
    sdk_options = {}
    for build_option in build_options:
        cli_key, cli_val = split_build_option(build_option)
        if cli_key not in cli_sdk_mapping:
            raise KeyError('Not supported build option.')
        sdk_key = cli_sdk_mapping[cli_key][0]
        parse_func = cli_sdk_mapping[cli_key][1]
        parse_func(sdk_options, sdk_key, cli_val)
    return sdk_options
