def wait_for_set_var(obj, attribute):
    while True:
        if hasattr(obj, attribute):
            break