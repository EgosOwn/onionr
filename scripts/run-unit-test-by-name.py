#!/usr/bin/env python3
import os
from time import sleep

input("enter to continue")  # hack to avoid vscode term input

test = input("test file name:")
if not test.endswith('.py'):
    test += '.py'

if os.path.exists(f'tests/{test}'):
    try:
        while True:
            os.system(f'python3 tests/{test}')
            if input("Enter to run again or n to stop:").lower().strip() == 'n':
                break
    except KeyboardInterrupt:
        pass
else:
    print('No test found')
