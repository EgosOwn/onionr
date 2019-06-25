import sqlite3, os
import onionrevents as events
from onionrutils import localcommand, epoch

def daemon_queue(core_inst):
    '''
        Gives commands to the communication proccess/daemon by reading an sqlite3 database

        This function intended to be used by the client. Queue to exchange data between "client" and server.
    '''

    retData = False
    if not os.path.exists(core_inst.queueDB):
        core_inst.dbCreate.createDaemonDB()
    else:
        conn = sqlite3.connect(core_inst.queueDB, timeout=30)
        c = conn.cursor()
        try:
            for row in c.execute('SELECT command, data, date, min(ID), responseID FROM commands group by id'):
                retData = row
                break
        except sqlite3.OperationalError:
            core_inst.dbCreate.createDaemonDB()
        else:
            if retData != False:
                c.execute('DELETE FROM commands WHERE id=?;', (retData[3],))
        conn.commit()
        conn.close()

    events.event('queue_pop', data = {'data': retData}, onionr = core_inst.onionrInst)

    return retData

def daemon_queue_add(core_inst, command, data='', responseID=''):
    '''
        Add a command to the daemon queue, used by the communication daemon (communicator.py)
    '''

    retData = True

    date = epoch.get_epoch()
    conn = sqlite3.connect(core_inst.queueDB, timeout=30)
    c = conn.cursor()
    t = (command, data, date, responseID)
    try:
        c.execute('INSERT INTO commands (command, data, date, responseID) VALUES(?, ?, ?, ?)', t)
        conn.commit()
    except sqlite3.OperationalError:
        retData = False
        core_inst.daemonQueue()
    events.event('queue_push', data = {'command': command, 'data': data}, onionr = core_inst.onionrInst)
    conn.close()
    return retData

def daemon_queue_get_response(core_inst, responseID=''):
    '''
        Get a response sent by communicator to the API, by requesting to the API
    '''
    assert len(responseID) > 0
    resp = localcommand.local_command(core_inst, 'queueResponse/' + responseID)
    return resp

def clear_daemon_queue(core_inst):
    '''
        Clear the daemon queue (somewhat dangerous)
    '''
    conn = sqlite3.connect(core_inst.queueDB, timeout=30)
    c = conn.cursor()

    try:
        c.execute('DELETE FROM commands;')
        conn.commit()
    except:
        pass

    conn.close()
    events.event('queue_clear', onionr = core_inst.onionrInst)