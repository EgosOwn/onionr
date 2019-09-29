import zipfile
def get_zip_site_file(path):
    with zipfile.ZipFile(zip_file, 'r') as zf:
        for member in zf.infolist():