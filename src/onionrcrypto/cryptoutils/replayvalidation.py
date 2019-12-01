from onionrutils import epoch
def replay_timestamp_validation(timestamp):
    return epoch.get_epoch() - int(timestamp) <= 2419200