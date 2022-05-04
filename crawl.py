import time
import os
from urllib.parse import urlparse,urljoin

import requests
from requests import Session
from bs4 import BeautifulSoup as bs

def check_errors(request):
    def inner_func(cls, method, url, **kwargs):
        request_success = False
        while not request_success:
            try:
                start = time.time()
                print(f'Trying to {method} data from {url}...')
                response = request(cls, method, url, **kwargs)
                time_elapsed = time.time() - start
                print(
                    f'The response from the server after {time_elapsed:.2f} seconds '\
                    f'was {len(response.text)} characters big. URL: {response.url}'
                )
                response.raise_for_status()
            except (
                    requests.exceptions.ConnectionError, requests.exceptions.SSLError
            ):
                print('Something went wrong. Retrying...')
                print(
                    f'Server URL: {url}), failed while trying to connect.'
                )
            except requests.exceptions.HTTPError:
                raw_response = response.content[:20] if len(response.content) > 50 else response.content
                try:
                    payload = kwargs['data']
                except KeyError:
                    payload = 'none'
                error_message = f'Server URL: {response.url}, ' \
                    f'failed with status code ({response.status_code}). ' \
                    f'Raw response: {raw_response}' \
                    f'Request payload: {payload}'

                print(error_message)
                if response.status_code < 499:
                    # return if client error
                    request_success = True
            else:
                request_success = True
            time.sleep(0.2)
        return response
    return inner_func

class Session(Session):
    """
    Overrriden version of requests.Session that checks for errors
    after completing the request.
    """

    @check_errors
    def request(self, method, url, **kwargs):
        return super().request(method, url, **kwargs)

session = Session()

def load_links(path):
    with open(path) as file:
        data = file.read()
    return data.split("\n")

def dump_link(url, path):
    with open(path, 'a') as file:
        file.write(url + "\n")

def get_file(url, remote_file):
    file_name = url.split('/')[-1]
    o = urlparse(url)
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
        link.remove(url)
        return -1

    response = session.get(url)
    html_doc = response.text
    get_file(url, html_doc)

    visited.add(url)
    dump_link(url, path="visited.txt")

    #If link returns an HTML page then parse using BeautifulSoup
    if url.find('.html') + 1:
        soup = bs(html_doc)
    else:
        return

    hRefs = set(soup.find_all('a'))
    for hRef in hRefs:
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
                    u = o.geturl()
                    if u not in visited:
                        if u not in links:
                            print(f"Added {u} to the queue")
                            link.add(u)
                            dump_link(u, "dumps.txt")
                        else:
                            print(f"Collected duplicate- {u}")
                            link_collect(u)

    ext_files = soup.find_all('link') + soup.find_all('script')
    for j in set(ext_files):
        try:
            temp = j['src']
        except KeyError:
            try:
                temp = j['href']
            except KeyError:
                continue
        temp1 = urljoin(url, temp)
        if temp1 in visited:
            continue
        if temp.startswith("_static"):
            link_collect(temp1)
            print(f"Collected static {temp1}")
            continue
        print(f"Added {u} to the queue")
        if temp1 not in link:
            link.add(temp1)
            dump_link(temp1, "dumps.txt")
        else:
            # it's already there
            # collect the duplicate
            link_collect(temp1)
            print(f"Collected duplicate {temp1}")

if __name__ == "__main__":
    location = '/var/www/pydocs/'

    link = set() 
    links = load_links("dumps.txt")
    if any(links):
        link.update(links)
    else:
        link.add('http://docs.python.org/tutorial/datastructures.html')

    visited = set()
    already_visited = load_links(path="visited.txt")
    if any(already_visited):
        visited.update(already_visited)
    while True:
        try:
            l = next(iter(link))
        except IndexError:
            break
        i = link_collect(l)
        if i != -1:
            print(f"{len(visited)} pages been mirrored already.")
