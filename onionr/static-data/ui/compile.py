#!/usr/bin/python3

import shutil, os, re, json, traceback

# get user's config
settings = {}
with open('config.json', 'r') as file:
    settings = json.loads(file.read())

# "hardcoded" config, not for user to mess with
HEADER_FILE = 'common/header.html'
FOOTER_FILE = 'common/footer.html'
SRC_DIR = 'src/'
DST_DIR = 'dist/'
HEADER_STRING = '<header />'
FOOTER_STRING = '<footer />'

# remove dst folder
shutil.rmtree(DST_DIR, ignore_errors=True)

# taken from https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

# copy src to dst
copytree(SRC_DIR, DST_DIR, False)

# load in lang map
langmap = {}

with open('lang.json', 'r') as file:
    langmap = json.loads(file.read())[settings['language']]

LANG = type('LANG', (), langmap)

# templating
def jsTemplate(template):
    with open('common/%s.html' % template, 'r') as file:
        return file.read().replace('\\', '\\\\').replace('\'', '\\\'').replace('\n', "\\\n")

def htmlTemplate(template):
    with open('common/%s.html' % template, 'r') as file:
        return file.read()

# tag parser
def parseTags(contents):
    # <$ logic $>
    for match in re.findall(r'(<\$(?!=)(.*?)\$>)', contents):
        try:
            out = exec(match[1].strip())
            contents = contents.replace(match[0], '' if out is None else str(out))
        except Exception as e:
            print('Error: Failed to execute python tag (%s): %s\n' % (filename, match[1]))
            traceback.print_exc()
            print('\nIgnoring this error, continuing to compile...\n')

    # <$= data $>
    for match in re.findall(r'(<\$=(.*?)\$>)', contents):
        try:
            out = eval(match[1].strip())
            contents = contents.replace(match[0], '' if out is None else str(out))
        except NameError as e:
            name = match[1].strip()
            print('Warning: %s does not exist, treating as an str' % name)
            contents = contents.replace(match[0], name)
        except Exception as e:
            print('Error: Failed to execute python tag (%s): %s\n' % (filename, match[1]))
            traceback.print_exc()
            print('\nIgnoring this error, continuing to compile...\n')

    return contents

# get header file
with open(HEADER_FILE, 'r') as file:
    HEADER_FILE = file.read()
    if settings['python_tags']:
        HEADER_FILE = parseTags(HEADER_FILE)

# get footer file
with open(FOOTER_FILE, 'r') as file:
    FOOTER_FILE = file.read()
    if settings['python_tags']:
        FOOTER_FILE = parseTags(FOOTER_FILE)

# iterate dst, replace files
def iterate(directory):
    for filename in os.listdir(directory):
        if filename.split('.')[-1].lower() in ['htm', 'html', 'css', 'js']:
            try:
                path = os.path.join(directory, filename)
                if os.path.isdir(path):
                    iterate(path)
                else:
                    contents = ''
                    with open(path, 'r') as file:
                        # get file contents
                        contents = file.read()

                    os.remove(path)

                    with open(path, 'w') as file:
                        # set the header & footer
                        contents = contents.replace(HEADER_STRING, HEADER_FILE)
                        contents = contents.replace(FOOTER_STRING, FOOTER_FILE)

                        # do python tags
                        if settings['python_tags']:
                            contents = parseTags(contents)

                        # write file
                        file.write(contents)
            except Exception as e:
                print('Error: Failed to parse file: %s\n' % filename)
                traceback.print_exc()
                print('\nIgnoring this error, continuing to compile...\n')

iterate(DST_DIR)
