import hashlib
import sys
from functools import wraps


def with_telemetry(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
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
            Output().error('Error: {0}'.format(str(e)))
            telemetry.fail(str(e), 'Command failed')
            telemetry.flush()
            sys.exit(1)

    return _wrapper


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
        is_none = '='
        if value is not None:
            is_none = '!='
        params.append('{0}{1}None'.format(key, is_none))
    return params


def hash256_result(func):
    """Secure the return string of the annotated function with SHA256 algorithm. If the annotated
    function doesn't return string or return None, raise ValueError."""
    @wraps(func)
    def _decorator(*args, **kwargs):
        val = func(*args, **kwargs)
        if not val:
            raise ValueError('Return value is None')
        elif not isinstance(val, str):
            raise ValueError('Return value is not string')
        hash_object = hashlib.sha256(val.encode('utf-8'))
        return str(hash_object.hexdigest())
    return _decorator
