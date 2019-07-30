from . import identifyhome
import filepaths
def get_hostname():
    try:
        with open(identifyhome.identify_home() + '/hs/hostname', 'r') as hostname:
            return hostname.read().strip()
    except FileNotFoundError:
        return "Not Generated"
    except Exception:
        return None