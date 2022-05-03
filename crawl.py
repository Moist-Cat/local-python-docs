import os
from collections import deque
#from urlparse import ...
from urllib.parse import urlparse,urljoin

from requests import Session
from bs4 import BeautifulSoup as bs

session = Session()

LINKS_FILE = 'dumps.txt'

def load_links(path=LINKS_FILE):
    with open(path) as file:
        data = file.read()
    return data.split("\n")

def dump_link(link, path=LINKS_FILE):
    with open(path, 'a') as file:
        file.write(link + "\n")

def get_file(url, remote_file):
    file_name = url.split('/')[-1]
    o = urlparse(url)
#    temp = o.path
    temp = o.path
    temp = location + temp
    ind = temp.find(file_name)
    temp1 = temp[:ind]
    if not os.path.exists(temp1):
        os.makedirs(temp1)
    ext = open(temp, 'w')
    ext.write(remote_file)
    ext.close()


def link_collect(url):
    if url in visited:
        #Visited link removed from list to prevent infinite loopi
        link.remove(url)
        return -1
    visited.append(url)
#    response = urllib2.urlopen(url)
    response = session.get(url)
#    html_doc = response.read()
    html_doc = response.text
#    get_file(url,html_doc)
    get_file(url, html_doc)
    #If link returns an HTML page then parse using BeautifulSoup
    if url.find('.html') + 1:
        soup = bs(html_doc)
    else:
        return
    for hRef in soup.find_all('a'):
        print(hRef)
        try:
            #If link doesn't have href attribute then continue
            hRef['href']
        except KeyError:
            continue
        else:
            #If link obtained is an inline link then ignore
            if hRef['href'].find('#') + 1:
                continue
            elif hRef['href'].find('.html') + 1:
                temp = hRef.get('href')
               	#Used to get details about the link such as the host name, url, etc.
                o = urlparse(urljoin(url,temp))
                if o.netloc == 'docs.python.org':
                    url = o.geturl()
                    if url not in visited:
                        link.append(o.geturl())
                        dump_link(url)
            ext_files = soup.find_all('link') + soup.find_all('script')
            for j in ext_files:
                try:
                    temp = j['src']
                except KeyError:
                    try:
                        temp = j['href']
                    except KeyError:
                        continue
                temp1 = urljoin(url,temp)
                if temp1 in visited:
                    continue
                else:
                    link.append(temp1)
                    dump_link(temp1)



if __name__ == "__main__":
    location = '/var/www/pydocs/'
    link = deque()
    old_links = load_links()
    if any(old_links):
        link.extend(old_links)
    else:
        link.append('http://docs.python.org/tutorial/datastructures.html')
    visited = []
    while (link):
        print(link[0])
        i = link_collect(link[0])
        try:
            link.popleft()
        except IndexError:
            break
        else:
            if i!=-1:
                print(len(visited))
