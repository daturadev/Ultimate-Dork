# -*- coding: utf-8 -*-
import json
import os
import random


def load_config(path='config.json'):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def random_proxy(config):
    proxies = config.get('proxies', [])
    return random.choice(proxies) if proxies else None


def random_user_agent(config):
    agents = config.get('user_agents', [])
    if agents:
        return random.choice(agents)
    from .useragent import useragent
    return useragent()
