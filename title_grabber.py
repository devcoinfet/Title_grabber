#!/usr/bin/env python3
#-*-coding:utf8;-*-

#qpy:3
#qpy:console

''' 
Extract the title from a web page using
the standard lib.
'''
import requests
import json
import os
from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.error import URLError
from threading import Thread, Lock
from multiprocessing import Process, cpu_count
PROCESS =  cpu_count() * 2
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
THREADS = 4
lock = Lock() 

found_titles = []
herders = {'headers':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''
        self._in_title_tag = False

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._in_title_tag = True

    def handle_data(self, data):
        if self._in_title_tag:
            self.title += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title_tag = False


def get_ips(dataset_path):
    
    ips = []

    file = open(dataset_path, "r")
    dataset = list(filter(None, file.read().split("\n")))
    
    for line in dataset:
        #line = json.loads(line)
        #ips.append(line['IP'])
        ips.append(line.rstrip())
        print(line)

    return ips



def ip_to_process(a, n):
    #ode to devil the best coder i know ;)
    k, m = divmod(len(a), n)
    for i in range(n):
        yield a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)]

def get_title(url):
    try:
        with urlopen(url,timeout=3) as stream:
            data = stream.read()
    except URLError:
        return

    parser = Parser()
    parser.feed(data.decode('utf-8', errors='ignore'))
    return parser.title


def get_server_info(url):
    try:
       response = requests.get(url,timeout=3,verify=False,headers=herders)
       cookies = response.headers['Set-Cookie']
       if cookies:
          return response.headers['Server'],cookies

       else:
           return response.headers['Server'],"No Cookies Set"
       
    except:
        pass


def title_grabber(urls):
    json_info = {}
    global found_titles
    for url in set(urls):
        try:
           title_info = get_title(url)
           if title_info:
              server_headers,cookies = get_server_info(url)
              title_grab = {}
              title_grab['url'] = url
              title_grab['title'] = title_info
              title_grab['server_headers'] = server_headers
              title_grab['cookies'] = cookies
              json_info = json.dumps(title_grab)
           try:
              for item in found_titles:
                  for key,value in item.items():
                      if key == url:
                          pass
                      else:
                          found_titles.append(json_info)
              

           except Exception as titlexc:
             pass

              
        except Exception as ohno:
           pass
           

if __name__ == "__main__":
    
   ip_list = get_ips("targets.txt")
   ips = ip_to_process(ip_list,PROCESS)
   for _ in range(PROCESS):
       p = Thread(target=title_grabber, args=(next(ips), ))
       p.daemon = True
       p.start()

   for _ in range(PROCESS):
       p.join()


