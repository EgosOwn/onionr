def get_client_API_server(core_inst):
    retData = ''
    try:
        with open(core_inst.privateApiHostFile, 'r') as host:
            hostname = host.read()
    except FileNotFoundError:
        raise FileNotFoundError
    else:
        retData += '%s:%s' % (hostname, core_inst.config.get('client.client.port'))
    return retData