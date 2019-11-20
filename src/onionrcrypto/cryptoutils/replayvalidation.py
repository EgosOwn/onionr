from onionrutils import epoch
def replay_timestamp_validation(timestamp):
    if epoch.get_epoch() - int(timestamp) > 2419200:
        return False
    else:
        return True