#-*- coding: utf-8 -*-
import sys, argparse
if sys.version[0] in '2':
   print('\n[x] Not Supported For python 2.x Please Use Python 3.x \n')
   exit()
from lib.tmp import color as _
try:
    import camoufox
    import requests
except Exception as e:
    print('\n{}[-]{} camoufox package Not Installed\n'.format(_.R,_.W))
    print('type pip3 install camoufox')
    exit()

from concurrent.futures import ThreadPoolExecutor, as_completed
from lib.lib import Parser
from lib.sqlscan import sqli_scan
from lib.tmp import logo
from lib.tmp import color as c
from lib.config import load_config, random_proxy, random_user_agent

urls = []

class crawl(object):

      auth = {
        1:[
            'https://www.google.com',
            'class="r"><a href="/url\?q=(.*?)&amp',
            'fl'
        ],
        2:[
            'https://www.bing.com',
            'h=".*?" href="(h.*?")',
            "b_widePag sb_bp"
        ]
      }

      def __init__(
        self,
        dork,
        proxy = None,
        user_agent = None
      ):
          self.dork = dork
          self.proxy = proxy
          self.user_agent = user_agent

      def Bing(self):
          bing = Parser(
            self.dork,
            crawl.auth[2][0],
            crawl.auth[2][1],
            crawl.auth[2][2],
            proxy = self.proxy,
            user_agent = self.user_agent
          )
          bing.request()
          for url in dir(bing):
              if 'go.microsoft.com' in url or 'bing.com' in url:
                  pass
              else:
                  urls.append(url)

      def Google(self):
          google = Parser(
            self.dork,
            crawl.auth[1][0],
            crawl.auth[1][1],
            crawl.auth[1][2],
            proxy = self.proxy,
            user_agent = self.user_agent
          )
          google.request()
          for url in dir(google):
              if 'go.microsoft.com' in url or 'bing.com' in url:
                 pass
              else:
                 urls.append(url)

class SQLi_Scanner(sqli_scan):
      pass

if sys.version[0] in '2':
   print('\n[x] Not Supported For python 2.x Please Use Python 3.x \n')
   exit()
fel = sys.argv[0]
par = argparse.ArgumentParser(
prog=fel,
usage="%(prog)s --dork [keyword]  --scan",
formatter_class=argparse.RawTextHelpFormatter,
description="""
Descriptions:
 * By : 407 Authentic Exploit
-----------------------------:
- Codename : JaxBCD
+ Crawl Web Use Google Dork & Bing Dork
+ with Features SQLi Scanner Vulnerability

""")

par.add_argument(
'--dork',
help="""
Your Dork e.g inurl:.php?id=

""",
metavar='[keywords]',
type=str)
par.add_argument(
'--proxy',
help='''
if using proxy e.g 127.0.0.1:1337
with auth e.g user@pass:127.0.0.1:1337

''',
metavar='[proxy:port]',
type=str,
action='store',
default=None)
par.add_argument(
'--config',
help='''
Path to config.json for proxy rotation, user agents, default URIs and thread count
(default: config.json)

''',
metavar='[path]',
type=str,
action='store',
default='config.json')
par.add_argument(
'--scan',help="if with Scan SQL injection Vulnerability Use This argument",action="store_true")
arg = par.parse_args()

# Load config and resolve effective settings
cfg = load_config(arg.config)
max_threads = cfg.get('max_threads', 1)
default_uris = cfg.get('default_uris', [])

def get_proxy():
    if arg.proxy:
        return arg.proxy
    return random_proxy(cfg)

def get_user_agent():
    return random_user_agent(cfg)

def run_scan(url):
    proxy = get_proxy()
    try:
        SQLi_Scanner().scan(url, proxy=proxy)
    except Exception as e:
        print(e)

try:
    if arg.scan:
       if arg.dork is not None:
           print(logo())
           _ = crawl(arg.dork, proxy=get_proxy(), user_agent=get_user_agent())
           _.Bing()
           _.Google()
           scan_targets = list(set(urls)) or default_uris
           if scan_targets:
              for url in scan_targets:
                  print('- {}'.format(url))
              with ThreadPoolExecutor(max_workers=max_threads) as executor:
                  futures = {executor.submit(run_scan, url): url for url in scan_targets}
                  for future in as_completed(futures):
                      try:
                          future.result()
                      except Exception as e:
                          print(e)
           else:
              print('\n{}[-]{} No Url Found !\n'.format(c.R,c.W))
       elif default_uris:
           print(logo())
           scan_targets = default_uris
           print('\n{}[*]{} Scanning default URIs from config...\n'.format(c.Y,c.W))
           for url in scan_targets:
               print('- {}'.format(url))
           with ThreadPoolExecutor(max_workers=max_threads) as executor:
               futures = {executor.submit(run_scan, url): url for url in scan_targets}
               for future in as_completed(futures):
                   try:
                       future.result()
                   except Exception as e:
                       print(e)
       else:
           par.print_help()
    elif not arg.scan:
       if arg.dork is not None:
          print(logo())
          _ = crawl(arg.dork, proxy=get_proxy(), user_agent=get_user_agent())
          _.Bing()
          _.Google()
          if urls:
             for url in list(set(urls)):
                 print('- {}'.format(url))
          else:
             print('\n{}[-]{} No Url Found !\n'.format(c.R,c.W))
       else:
          par.print_help()
    else:
       par.print_help()
except Exception as e:
    print(e)
except KeyboardInterrupt:
    exit()
