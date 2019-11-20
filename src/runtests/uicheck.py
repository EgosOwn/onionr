from onionrutils import localcommand
def check_ui(test_manager):
    endpoints = ['/', '/mail/', '/friends/', '/board/']
    for point in endpoints:
        result = localcommand.local_command(point)
        if not result: raise ValueError
        result = result.lower()
        if not 'script' in result:
            raise ValueError(f'uicheck failed on {point}')
