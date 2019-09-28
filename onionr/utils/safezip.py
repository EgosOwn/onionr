# safe unzip https://stackoverflow.com/a/36583849
def safe_unzip(zip_file, extractpath='.'):
    with zipfile.ZipFile(zip_file, 'r') as zf:
        for member in zf.infolist():
            abspath = os.path.abspath(os.path.join(extractpath, member.filename))
            if abspath.startswith(os.path.abspath(extractpath)):
                zf.extract(member, extractpath)
