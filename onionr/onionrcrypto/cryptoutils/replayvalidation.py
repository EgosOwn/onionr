import utils # onionr utils epoch, not this utils
def replay_timestamp_validation(timestamp):
    if utils.epoch.get_epoch() - int(timestamp) > 2419200:
        return False
    else:
        return True