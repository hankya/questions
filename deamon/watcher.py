import sys
import os
import time
from subprocess import Popen
from redis import StrictRedis
redis_cli = StrictRedis(host='localhost', port=6379, db=0)
logfile = 'logs/%s%s' % (para, time.strftime('%Y-%m-%d', time.gmtime()))
logpara= 'LOG_FILE=%s' % logfile
p = Popen(['scrapy','crawl',para,'-s',logpara])
while True:
    p.wait()
    p = Popen(['scrapy','crawl',para,'-s',logpara])
    print 'new process has been spawned %s' % p.pid
    
def is_process_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    
def is_running(p):
    try:
        code = p.poll()
        if code == None:
            return False
        return True
    except OSError:
        return False

def main(p, pra):
    state = is_running(p)
    while True:
        if not state:
            p.wait()            
            p = Popen(['scrapy','crawl',pra])
            print 'created new process %s' % p.pid
            
        proxies = redis_cli.scard('proxies_%s' % pra)
        if proxies < 10:
            os.kill(pid, 15)
        time.sleep(30)
        state = is_running(p)
        
        
        print 'sleeping for 30 seconds'
                    
if __name__ == '__main__':
    main(sys.argv)
