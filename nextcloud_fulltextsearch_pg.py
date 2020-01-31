#!/usr/bin/env python

#
# My comments (placeholder)
#

from optparse import OptionParser
import sys
import time
import re
import os
import numbers

try:
    import psycopg2
except ImportError as e:
    print(e)
    sys.exit(2)


def performance_data(perf_data, params):
    data = ''
    if perf_data:
        data = " |"
        for p in params:
            p += (None, None, None, None)
            param, param_name, warning, critical = p[0:4]
            data += "%s=%s" % (param_name, str(param))
            if warning or critical:
                warning = warning or 0
                critical = critical or 0
                data += ";%s;%s" % (warning, critical)

            data += " "

    return data


def numeric_type(param):
    return param is None or isinstance(param, numbers.Real)


def check_levels(param, warning, critical, message, ok=[]):
    if (numeric_type(critical) and numeric_type(warning)):
        if warning >= critical:
            print("WARNING - The warning threshold is greater than critical threshold")
            sys.exit(1)
        elif param >= critical:
            print("CRITICAL - " + message)
            sys.exit(2)
        elif param >= warning:
            print("WARNING - " + message)
            sys.exit(1)
        else:
            print("OK - " + message)
            sys.exit(0)
    else:
        if param in critical:
            print("CRITICAL - " + message)
            sys.exit(2)

        if param in warning:
            print("WARNING - " + message)
            sys.exit(1)

        if param in ok:
            print("OK - " + message)
            sys.exit(0)

        # unexpected param value
        print("CRITICAL - Unexpected value : %d" % param + "; " + message)
        return 2

def main(argv=None):

    p = OptionParser()
    p.add_option('-H', '--host', action='store', type='string', dest='host', default='127.0.0.1', help='The hostname of postgres database')
    p.add_option('-d', '--database', action='store', type='string', dest='database', default='postgres', help='The nextcloud database the fulltextsearch table is inside')
    p.add_option('-u', '--user', action='store', type='string', dest='user', default='nextcloud', help='The user which has access to nextcloud database')
    p.add_option('-p', '--password', action='store', type='string', dest='password', default='', help='The password of nextcloud db user')
    p.add_option('-P', '--port', action='store', type='string', dest='port', default='5432', help='The port of nextcloud database')
    p.add_option('-D', '--perf-data', action='store_true', dest='perf_data', default=False, help='Enable output of Nagios performance data')
    p.add_option('-A', '--action', type='choice', dest='action', default='connect', help='The action the script should execute',
                    choices=['fts_queue', 'fts_errors', 'connect']
                )
    p.add_option('-w', '--warning', action='store', dest='warning', default=None, help='Warning threshold')
    p.add_option('-c', '--critical', action='store', dest='critical', default=None, help='Critical threshold')

    options, arguments = p.parse_args()
    host = options.host
    database = options.database
    user = options.user
    password = options.password
    port = options.port
    perf_data = options.perf_data
    action = options.action
    warning = int(options.warning or 0)
    critical = int(options.critical or 0)

    # connect to the databse, create cursor and determine connection time
    start = time.time()
    con = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    cur = con.cursor()
    conn_time = time.time() - start


    if action == "fts_queue":
        return check_fts_queue(cur, warning, critical, perf_data)
    elif action == "fts_errors":
        return check_fts_error(cur, warning, critical, perf_data)
    else:
        return check_connect(host, port, database, user, password, warning, critical, conn_time, perf_data)


def check_connect(host, port, database, user, password, warning, critical, conn_time, perf_data):
    warning = warning or 3
    critical = critical or 6
    message = "Connection took %.3f seconds" % conn_time
    message += performance_data(perf_data, [(conn_time, "connection_time", warning, critical)])
    return check_levels(conn_time, warning, critical, message)


def check_fts_queue(cur, warning, critical, perf_data):
    warning = warning or 10
    critical = critical or 50
    cur.execute("""select  * from oc_fulltextsearch_indexes where status != 1;""")
    rows = cur.fetchall()

    fts_queue = 0

    for row in rows:
      fts_queue += 1

    message = "Documents in queue: %d" % fts_queue
    message += performance_data(perf_data, [("%d" % fts_queue, "documents_pending", warning, critical)])
    cur.close()
    return check_levels(fts_queue, warning, critical, message)


def check_fts_error(cur, warning, critical, perf_data):
    warning = warning or 1
    critical = critical or 2
    cur.execute("""select  * from oc_fulltextsearch_indexes where err != 0;""")
    rows = cur.fetchall()

    fts_errors = 0

    for row in rows:
      fts_errors += 1

    message = "Index errors: %d" % fts_errors
    message += performance_data(perf_data, [("%d" % fts_errors, "index_erros", warning, critical)])
    cur.close()
    return check_levels(fts_errors, warning, critical, message)



    con.close()
if __name__ == "__main__":
    main(sys.argv)
