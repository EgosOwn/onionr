#!/usr/bin/env python3

"""Enable dev default config"""

import json

conf = json.load(open('static-data/default_config.json', 'r'))
json.dump(conf, open('static-data/default_config.json', 'w'), sort_keys=True, indent=4)
print("Tidied default config")
