# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import load_config, random_proxy, random_user_agent
from .sqlscan import sqli_scan


class crawl:
    auth = {
        1: [
            'https://www.google.com',
            r'class="r"><a href="/url\?q=(.*?)&amp',
            'fl',
        ],
        2: [
            'https://www.bing.com',
            r'h=".*?" href="(h.*?")',
            'b_widePag sb_bp',
        ],
    }

    def __init__(self, dork, proxy=None, user_agent=None, output_cb=None):
        self.dork = dork
        self.proxy = proxy
        self.user_agent = user_agent
        self.output_cb = output_cb or print
        self._urls = []

    def Bing(self):
        from .lib import Parser
        p = Parser(
            self.dork,
            self.auth[2][0],
            self.auth[2][1],
            self.auth[2][2],
            proxy=self.proxy,
            user_agent=self.user_agent,
            output_cb=self.output_cb,
        )
        p.request()
        for url in dir(p):
            if 'go.microsoft.com' not in url and 'bing.com' not in url:
                self._urls.append(url)

    def Google(self):
        from .lib import Parser
        p = Parser(
            self.dork,
            self.auth[1][0],
            self.auth[1][1],
            self.auth[1][2],
            proxy=self.proxy,
            user_agent=self.user_agent,
            output_cb=self.output_cb,
        )
        p.request()
        for url in dir(p):
            if 'go.microsoft.com' not in url and 'bing.com' not in url:
                self._urls.append(url)

    @property
    def urls(self):
        return list(set(self._urls))


class SQLiScanner(sqli_scan):
    pass


def run_dork(dork, proxy=None, config_path='config.json', scan=False,
             output_cb=None, stop_event=None):
    """Run a dork search and optionally scan results for SQLi.

    Args:
        dork:        Search query / dork string (None → use default_uris only).
        proxy:       Explicit proxy string; overrides config rotation.
        config_path: Path to config.json.
        scan:        Whether to run the SQLi scanner on found URLs.
        output_cb:   Callable that receives each output line (defaults to print).
        stop_event:  threading.Event; set it to request a clean abort.
    Returns:
        List of discovered URLs.
    """
    if output_cb is None:
        output_cb = print

    cfg = load_config(config_path)
    try:
        max_threads = max(1, int(cfg.get('max_threads', 1)))
    except (TypeError, ValueError):
        max_threads = 1
    default_uris = cfg.get('default_uris', [])

    def _proxy():
        return proxy or random_proxy(cfg)

    def _ua():
        return random_user_agent(cfg)

    def _scan_url(url):
        if stop_event and stop_event.is_set():
            return
        SQLiScanner().scan(url, proxy=_proxy(), output_cb=output_cb)

    targets = []
    if dork:
        c = crawl(dork, proxy=_proxy(), user_agent=_ua(), output_cb=output_cb)
        c.Bing()
        if not (stop_event and stop_event.is_set()):
            c.Google()
        targets = c.urls or default_uris
    else:
        targets = default_uris

    if not targets:
        output_cb('[-] No URLs found.\n')
        return []

    for url in targets:
        output_cb(f'- {url}')

    if scan:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(_scan_url, url): url for url in targets}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    output_cb(str(exc))

    return targets
