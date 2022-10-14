from types import ModuleType
from jsonrpc import dispatcher


def add_module_to_api(module: ModuleType):
    prefix = f"{module.__name__}."
    for attr in dir(module):
        attr = getattr(module, attr)
        if callable(attr):
            if hasattr(attr, 'json_compatible'):
                dispatcher[prefix + attr.__name__] = attr