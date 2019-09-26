from onionrutils import localcommand
def check_ui(test_manager):
    if not 'onionr' in localcommand.local_command('/mail/').lower(): raise AssertionError