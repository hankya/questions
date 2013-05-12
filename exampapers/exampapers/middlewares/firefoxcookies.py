class FirefoxCookiesMiddleware(CookiesMiddleware):
    def __init__(self, debug=False):
        
        super(FirefoxCookiesMiddleware, self).__init__(debug)
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        
    def spider_opened(self, spider):
        jar = self.jars[None]
        jar.jar._cookies =  sqlite2cookie()._cookies
        
def sqlite2cookie(filename='/home/user/.mozilla/firefox/q0kuegus.default/cookies.sqlite'):
    from cStringIO import StringIO
    from pysqlite2 import dbapi2 as sqlite
    import cookielib
    #programtically get the cookie filepath
    filename = _get_firefox_cookie_path()
    
    with sqlite.connect(filename) as con:
        cur = con.cursor()
        cur.execute("select host, path, isSecure, expiry, name, value from moz_cookies")
        ftstr = ["FALSE","TRUE"]    
        s = StringIO()
        s.write("""\
# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
""")
        for item in cur.fetchall():
            s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                item[0], ftstr[item[0].startswith('.')], item[1],
                                  ftstr[item[2]], item[3], item[4], item[5]))
                
        s.seek(0)
        cookie_jar = cookielib.MozillaCookieJar()
        cookie_jar._really_load(s, '', True, True)
        return cookie_jar

import os
import ConfigParser        
def _get_firefox_cookie_path():
    homedir = os.path.expanduser('~')
    firefoxdir = os.path.join(homedir, '.mozilla/firefox')
    profiles_ini = os.path.join(firefoxdir, 'profiles.ini')
    if not os.path.exists(profiles_ini):
        return None

    profiles_ini_reader = ConfigParser.ConfigParser()
    profiles_ini_reader.readfp(open(profiles_ini))
    profile_name = profiles_ini_reader.get('Profile0', 'Path', True)
    
    profile_path = os.path.join(firefoxdir, profile_name)
    if not os.path.exists(profile_path):
        return None
    else:
        if os.path.join(profile_path, 'cookies.sqlite'):
            return os.path.join(profile_path, 'cookies.sqlite')
        elif os.path.join(profile_path, 'cookies.txt'):
            return os.path.join(profile_path, 'cookies.txt')
