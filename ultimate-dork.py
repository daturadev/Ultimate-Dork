#-*- coding: utf-8 -*-
import sys
import argparse

if sys.version[0] in '2':
    print('\n[x] Not Supported For python 2.x Please Use Python 3.x\n')
    exit()

from lib.tmp import color as _, logo

try:
    import camoufox
    import requests
except ImportError:
    print('\n{}[-]{} camoufox or requests not installed\n'.format(_.R, _.W))
    print('  pip install -r requirements.txt')
    print('  python -m camoufox fetch')
    exit()

from lib.core import run_dork

par = argparse.ArgumentParser(
    prog=sys.argv[0],
    usage='%(prog)s --dork [keyword] [--scan] [--proxy proxy] [--config path]',
    formatter_class=argparse.RawTextHelpFormatter,
    description="""
Descriptions:
 * By : 407 Authentic Exploit
-----------------------------:
- Codename : JaxBCD
+ Crawl Web using Google Dork & Bing Dork
+ with Features SQLi Scanner Vulnerability
""")

par.add_argument('--dork',   metavar='[keywords]',   type=str,
                 help='\nDork keyword  e.g. inurl:.php?id=\n\n')
par.add_argument('--proxy',  metavar='[proxy:port]', type=str, default=None,
                 help='\nProxy  e.g. 127.0.0.1:1337  or  socks5://host:port\n\n')
par.add_argument('--config', metavar='[path]',       type=str, default='config.json',
                 help='\nPath to config.json  (default: config.json)\n\n')
par.add_argument('--scan',   action='store_true',
                 help='Run SQLi vulnerability scan on discovered URLs')

arg = par.parse_args()

if not arg.dork:
    par.print_help()
    exit()

print(logo())
try:
    run_dork(
        dork=arg.dork,
        proxy=arg.proxy,
        config_path=arg.config,
        scan=arg.scan,
    )
except KeyboardInterrupt:
    print('\n[!] Interrupted')
    exit()
