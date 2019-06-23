import time, os
def is_communicator_running(core_inst, timeout = 5, interval = 0.1):
    try:
        runcheck_file = core_inst.dataDir + '.runcheck'

        if not os.path.isfile(runcheck_file):
            open(runcheck_file, 'w+').close()

        starttime = time.time()

        while True:
            time.sleep(interval)

            if not os.path.isfile(runcheck_file):
                return True
            elif time.time() - starttime >= timeout:
                return False
    except:
        return False