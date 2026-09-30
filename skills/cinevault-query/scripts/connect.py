#!/usr/bin/env python3
"""CineVault reader onboarding and local stdio-to-JSON-HTTP bridge (stdlib)."""
import argparse
import getpass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

TOOLS = {'search_titles', 'get_title', 'list_resources', 'get_stats'}
CONFIG = Path.home() / '.config' / 'cinevault' / 'reader.json'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

def valid_url(value):
    u = urllib.parse.urlsplit(value)
    if u.path != '/mcp' or u.query or u.fragment or u.username or u.password:
        raise ValueError('URL must end in /mcp without credentials or query parameters')
    if u.scheme != 'https' and not (u.scheme == 'http' and u.hostname in ('127.0.0.1', 'localhost', '::1')):
        raise ValueError('Use HTTPS, or loopback HTTP for a local test')
    return value

class Connection:
    def __init__(self, config):
        self.url = valid_url(config['url'])
        self.key = config['key']
        if not self.key or any(c.isspace() for c in self.key):
            raise ValueError('Invalid API Key format')
        self.session = None
        self.protocol = None
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, body):
        headers = {'Content-Type':'application/json', 'Accept':'application/json, text/event-stream', 'Authorization':'Bearer '+self.key}
        if self.session: headers['Mcp-Session-Id'] = self.session
        if self.protocol: headers['MCP-Protocol-Version'] = self.protocol
        req = urllib.request.Request(self.url, json.dumps(body).encode(), headers)
        with self.opener.open(req, timeout=20) as r:
            if r.headers.get('Mcp-Session-Id'): self.session = r.headers['Mcp-Session-Id']
            data = r.read(1048577)
            if len(data)>1048576: raise ValueError('Response too large')
            if not data: return None
            if 'text/event-stream' in r.headers.get('Content-Type',''):
                messages = [json.loads(line[5:].strip()) for line in data.decode().splitlines() if line.startswith('data:')]
                value = next((x for x in messages if x.get('id') == body.get('id')), None)
                if value is None: raise ValueError('Missing response')
            else: value = json.loads(data)
            if body.get('method') == 'initialize' and 'result' in value:
                self.protocol = value['result']['protocolVersion']
            return value

    def check(self):
        init = self.request({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'cinevault-reader-setup','version':'1.0.0'}}})
        if not init or 'error' in init: raise ValueError('Initialization rejected')
        self.request({'jsonrpc':'2.0','method':'notifications/initialized'})
        result = self.request({'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}})
        if not result or 'error' in result: raise ValueError('Tool discovery rejected')
        names = {t['name'] for t in result['result']['tools']}
        if names != TOOLS: raise ValueError('Endpoint must provide exactly the four reader tools')

def load(path):
    if path.stat().st_mode & 0o077: raise ValueError('Private config must have permissions 600')
    return json.loads(path.read_text())

def setup(args):
    if CONFIG.exists(): raise ValueError('Reader config already exists; use check, or back it up before replacing')
    if not shutil.which('codex'): raise ValueError('Codex CLI not found')
    current = subprocess.run(['codex','mcp','get','cinevault-query'],capture_output=True)
    if current.returncode == 0: raise ValueError('cinevault-query connection already exists; inspect it before changing')
    url = valid_url(args.url)
    if args.key_file:
        path = Path(args.key_file).expanduser()
        if path.stat().st_mode & 0o077: raise ValueError('API Key file must have permissions 600')
        key = path.read_text().strip()
    else:
        if not sys.stdin.isatty(): raise ValueError('Run setup in an interactive terminal, or specify a private --key-file')
        key = getpass.getpass('普通 API Key（隐藏输入，不会显示）: ').strip()
    config = {'url':url, 'key':key}
    Connection(config).check()
    CONFIG.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd = os.open(CONFIG,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f: json.dump(config,f)
    result = subprocess.run(['codex','mcp','add','cinevault-query','--',sys.executable,str(Path(__file__).resolve()),'serve'],capture_output=True)
    if result.returncode: raise ValueError('Credential saved, but registration failed; run register to retry')
    print('普通查询连接验证通过，4 个工具；已注册 cinevault-query。请在新聊天中继续查询。')

def serve():
    connection = Connection(load(CONFIG))
    for line in sys.stdin:
        ident = None
        try:
            if len(line)>1048576: raise ValueError('Request too large')
            body = json.loads(line); ident = body.get('id')
            method = body.get('method','')
            if method == 'tools/call' and body.get('params',{}).get('name') not in TOOLS:
                raise ValueError('Reader tool required')
            if method == 'ping':
                response = {'jsonrpc':'2.0','id':ident,'result':{}}
            elif method in ('initialize','tools/list','tools/call','notifications/initialized'):
                response = connection.request(body)
            elif ident is None: continue
            else: raise ValueError('Unsupported method')
            if ident is not None and response:
                print(json.dumps(response,ensure_ascii=False),flush=True)
        except Exception:
            if ident is not None:
                print(json.dumps({'jsonrpc':'2.0','id':ident,'error':{'code':-32603,'message':'CineVault connection failed; check configuration and authorization.'}}),flush=True)

def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('setup');p.add_argument('--url',required=True);p.add_argument('--key-file')
    sub.add_parser('check');sub.add_parser('serve');sub.add_parser('register')
    args=parser.parse_args()
    try:
        if args.command=='setup': setup(args)
        elif args.command=='serve': serve()
        elif args.command=='check':
            Connection(load(CONFIG)).check();print('普通 MCP 认证及 4 个查询工具验证通过；未执行数据写入。')
        else:
            Connection(load(CONFIG)).check()
            r=subprocess.run(['codex','mcp','get','cinevault-query'],capture_output=True)
            if r.returncode == 0: raise ValueError('Connection already exists; inspect it before changing')
            r=subprocess.run(['codex','mcp','add','cinevault-query','--',sys.executable,str(Path(__file__).resolve()),'serve'],capture_output=True)
            if r.returncode: raise ValueError('Registration failed')
            print('普通 MCP 已注册，请在新聊天中继续。')
    except urllib.error.HTTPError as e:
        print('连接失败：HTTP '+str(e.code)+'；401/403 请检查普通 Key 或授权。',file=sys.stderr);return 1
    except ValueError as e:
        print(str(e),file=sys.stderr);return 1
    except Exception:
        print('连接失败：检查服务状态、地址及私密配置；未输出凭据。',file=sys.stderr);return 1
    return 0

if __name__=='__main__': sys.exit(main())
