import math, time
def get_rounded_epoch(roundS=60):
    '''
        Returns the epoch, rounded down to given seconds (Default 60)
    '''
    epoch = get_epoch()
    return epoch - (epoch % roundS)

def get_epoch(self):
    '''returns epoch'''
    return math.floor(time.time())