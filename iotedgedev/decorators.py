import sys
from functools import wraps

import click

PARAMS_WITH_VALUES = {'edge_runtime_version'}

def with_telemetry(func):
    @wraps(func)
    def _wrapped_func(*args, **kwargs):
        from . import telemetry
        from .telemetryconfig import TelemetryConfig

        config = TelemetryConfig()
        config.check_firsttime()
        params = parse_params(*args, **kwargs)
        telemetry.start(func.__name__, params)
        try:
            value = func(*args, **kwargs)
            telemetry.success()
            telemetry.flush()
            return value
        except Exception as e:
            from .output import Output
            Output().error(str(e))
            telemetry.fail(str(e), 'Command failed')
            telemetry.flush()
            sys.exit(1)

    return _wrapped_func


def suppress_all_exceptions(fallback_return=None):
    """We need to suppress exceptions for some internal functions such as those related to telemetry.
    They should not be visible to users.
    """
    def _decorator(func):
        @wraps(func)
        def _wrapped_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                if fallback_return:
                    return fallback_return
                else:
                    pass

        return _wrapped_func

    return _decorator


@suppress_all_exceptions()
def parse_params(*args, **kwargs):
    """Record the parameter keys and whether the values are None"""
    params = []
    for key, value in kwargs.items():
        if (value is None) or (key in PARAMS_WITH_VALUES):
            params.append('{0}={1}'.format(key, value))
        else:
            params.append('{0}!=None'.format(key))
    return params


def hash256_result(func):
    """Secure the return string of the annotated function with SHA256 algorithm. If the annotated
    function doesn't return string or return None, raise ValueError."""
    @wraps(func)
    def _wrapped_func(*args, **kwargs):
        val = func(*args, **kwargs)
        if not val:
            raise ValueError('Return value is None')
        elif not isinstance(val, str):
            raise ValueError('Return value is not string')

        from .utility import Utility
        return Utility.get_sha256_hash(val)

    return _wrapped_func


def module_template_options(func):
    """Merge the module template option decorators into a single one."""
    template_dec = click.option("--template",
                                "-t",
                                default="csharp",
                                show_default=True,
                                required=False,
                                type=click.Choice(["c", "csharp", "java", "nodejs", "python", "csharpfunction"]),
                                help="Specify the template used to create the default module")
    group_id_dec = click.option("--group-id",
                                "-g",
                                default="com.edgemodule",
                                show_default=True,
                                help="(Java modules only) Specify the groupId")
    return template_dec(group_id_dec(func))


def add_module_options(envvars, init=False):
    """Decorate commands which involve adding modules to the solution."""
    """`init` specifies whether the command initializes a new solution."""
    if init:
        module_name_dec = click.option("--module",
                                       "-m",
                                       required=False,
                                       default=envvars.get_envvar("DEFAULT_MODULE_NAME", default="filtermodule"),
                                       show_default=True,
                                       help="Specify the name of the default module")
    else:
        module_name_dec = click.argument("name",
                                         required=True)

    def _decorator(func):
        return module_name_dec(module_template_options(func))

    return _decorator
