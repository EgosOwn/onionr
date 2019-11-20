from coredb import daemonqueue

def do_runtime_test():
    daemonqueue.daemon_queue_add("runtimeTest")

do_runtime_test.onionr_help = "If Onionr is running, initialize run time tests (check logs)"
