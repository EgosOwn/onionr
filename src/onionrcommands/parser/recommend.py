import sys
from difflib import SequenceMatcher
import logger
from . import arguments


def recommend(print_default: bool = True):
    tried = sys.argv[1]
    args = arguments.get_arguments()
    print_message = 'Command not found:'
    for key in args.keys():
        for word in key:
            if SequenceMatcher(None, tried, word).ratio() >= 0.75:
                logger.warn(f'{print_message} "{tried}", '
                            + 'did you mean "{word}"?',
                            terminal=True)
                return
    if print_default: logger.error('%s "%s"' %
                                   (print_message, tried), terminal=True)
