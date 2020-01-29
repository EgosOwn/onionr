from threading import Thread

from onionrutils import localcommand


def on_blacklist_add(api, data=None):
    blacklisted_data = data['data']

    def remove():
        localcommand.local_command(f'/mail/deletemsg/{blacklisted_data}', post=True)

    Thread(target=remove).start()
