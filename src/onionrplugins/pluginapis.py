#
from typing import Callable, Dict

# plugin apis are methods intended to be available to the rpc
# plugin, this is so plugins can provide apis to other plugins
# plugins add their methods during or before afterinit event
plugin_apis: Dict[str, Callable] = {}