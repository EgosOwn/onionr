import sys
from difflib import SequenceMatcher
import logger
from . import arguments

def recommend():
    tried = sys.argv[1]
    args = arguments.get_arguments()
    print_message = 'Command not found:'
    for key in args.keys():
        for word in key:
            if SequenceMatcher(None, tried, word).ratio() >= 0.75:
                logger.warn('%s "%s", did you mean "%s"?' % (print_message, tried, word), terminal=True)
                return
    logger.error('%s "%s"' % (print_message, tried), terminal=True)