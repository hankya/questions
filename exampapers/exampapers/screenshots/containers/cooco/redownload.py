import urllib


def get_file(url, filepath):
    sock = urllib.urlopen(url)
    data = sock.read()
    sock.close()
    with open(filepath, 'wb') as f:
        f.write(data)
        print '%s downloaded and saved' % filepath
        
        
'screenshots/containers/cooco
