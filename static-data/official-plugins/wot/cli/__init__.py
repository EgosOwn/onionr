import tty
import sys
import subprocess

def do_quit(): raise KeyboardInterrupt

def list_idens():
    print('Listing identities')


main_menu = {
    'l': (list_idens, 'list trusted identities'),
    'q': (do_quit, 'quit CLI')
}

def main_ui():
    tty.setraw(sys.stdin)

    while True:
        # move cursor to the beginning
        print('\r', end='')
        key = sys.stdin.read(1)
        try:
            main_menu[key][1]()
        except KeyError:
            pass
        except KeyboardInterrupt:
            break


    subprocess.Popen(['reset'], stdout=subprocess.PIPE)
