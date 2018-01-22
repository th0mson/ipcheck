#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, tempfile
import daemon, ipcheck
 
class IPCheck(daemon.Daemon):
    def run(self):
        c = ipcheck.IPCheck()

        # First message for start Daemon
        c.fireNotify('Monitoring up')

        while True:
            c.check()
            time.sleep(c.getDaemonTimeout())

if __name__ == '__main__':
    pidFile = tempfile.gettempdir() + '/ipcheck.pid'
    daemon = IPCheck(pidFile)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print 'Daemon starting..'
            daemon.start()
            print 'Daemon started!'
        elif 'stop' == sys.argv[1]:
            print 'Daemon stopping..'
            daemon.stop()
            print 'Daemon stopped!'
        elif 'restart' == sys.argv[1]:
            print 'Daemon restarting..' 
            daemon.restart()
            print 'Daemon restarted!' 
        else:
            print 'Unknown command' 
            sys.exit(2)
        sys.exit(0)
    else:
        print 'usage: %s start|stop|restart' % sys.argv[0] 
        sys.exit(2)