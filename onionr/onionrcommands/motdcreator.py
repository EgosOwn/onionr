import onionrblocks

def motd_creator():
    """Create a new MOTD message for the Onionr network"""
    motd = ''
    new = ''
    print('Enter a new MOTD, quit on a new line:')
    while new != 'quit':
        new = input()
        if new != 'quit':
            motd += new
    bl = onionrblocks.insert(motd, header='motd', sign=True)
    print(f"inserted in {bl}")

motd_creator.onionr_help = "Create a new MOTD message for the onionr network"
