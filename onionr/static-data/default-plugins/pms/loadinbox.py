import onionrblockapi
def load_inbox(myCore):
    inbox_list = []
    deleted = myCore.keyStore.get('deleted_mail')
    if deleted is None:
        deleted = []

    for blockHash in myCore.getBlocksByType('pm'):
        block = onionrblockapi.Block(blockHash, core=myCore)
        block.decrypt()
        if block.decrypted and blockHash not in deleted:
            inbox_list.append(blockHash)
    return inbox_list