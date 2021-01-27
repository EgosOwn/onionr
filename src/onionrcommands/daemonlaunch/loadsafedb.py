import safedb
import filepaths


def load_safe_db(config) -> safedb.SafeDB:
    return safedb.SafeDB(
        filepaths.main_safedb, config.get('security.encrypt_database', False))
