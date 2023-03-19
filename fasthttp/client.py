# -*- coding: utf-8 -*-
import six
import os
if six.PY2:
    import httplib as http_client
else:
    import http.client as http_client
if six.PY3:
    from urllib.parse import quote, urlparse, urlencode #python 3
else:   
    from urlparse import urlparse #python 2
    from urllib import quote, urlencode
if six.PY2:
    import Cookie as http_cookies
else:
    import http.cookies as http_cookies
if six.PY3:
    from io import BytesIO
else:
    from StringIO import StringIO as BytesIO
import gzip
import zlib
import json as json_
import sqlite3
import time
import ssl
import base64
import random

try:
    from kodi_six import xbmc, xbmcvfs
    translate = xbmcvfs.translatePath if six.PY3 else xbmc.translatePath
    cache = translate('special://home/addons/script.module.fasthttp/lib/fasthttp/cache.db')
except:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    cache = os.path.join(dir_path, "cache.db")

class _Property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.func(instance)
    
class HttpResponse_http_client(object):
    def __init__(self, r, url, conn_sqlite, c, h, cache_time,url_base64,cookies,method,payload):
        self.url = url
        self.r = r
        self.h = h
        self.cache_time = cache_time if cache_time else None
        self.conn_sqlite = conn_sqlite if conn_sqlite else None
        self.url_base64 = url_base64
        self.c = c if c else None
        self._cookies = cookies if cookies else {}
        self.method = method
        self.payload = payload if payload else None

    @_Property
    def status_code(self):
        return self.r.status
    
    @_Property
    def cookies(self):
        return self._cookies   

    @_Property
    def content(self):
        _content = self.r.read()
        if 'gzip' in self.h.get('Accept-Encoding', '').lower() or 'deflate' in self.h.get('Accept-Encoding', '').lower():
            try:
                buffer = BytesIO(_content)
                gzipper = gzip.GzipFile(fileobj=buffer)
                _content = gzipper.read()
            except:
                try:
                    _content = zlib.decompress(_content)
                except:
                    pass
        self.r.close()
        return _content        

    @_Property
    def text(self):
        content = self.r.read()
        if 'gzip' in self.h.get('Accept-Encoding', '').lower() or 'deflate' in self.h.get('Accept-Encoding', '').lower():
            try:
                buffer = BytesIO(content)
                gzipper = gzip.GzipFile(fileobj=buffer)
                content = gzipper.read()
            except:
                try:
                    content = zlib.decompress(content)
                except:
                    pass          
        try:
            content = content.decode()
        except:
            try:
                content = content.decode('utf-8')
            except:
                content = ''
        if self.cache_time and content:
            timestamp = time.time()
            if self.method == 'get':
                self.c.execute("REPLACE INTO cache_get (url, content, status_code, timestamp) VALUES (?, ?, ?, ?)", (self.url_base64, content, self.r.status, timestamp))
            elif self.method == 'post' and self.payload:
                self.c.execute("REPLACE INTO cache_post (url, payload, content, status_code, timestamp) VALUES (?, ?, ?, ?, ?)", (self.url_base64, self.payload, content, self.r.status, timestamp))
            self.conn_sqlite.commit()            
        self.r.close()     
        return content
    
    def iter_content(self,chunk_size=1024):
        try:
            remaining = int(self.r.getheader('Content-Length'))
            loop1 = True
        except:
            loop1 = False
        if loop1:  
            remaining = int(self.r.getheader('Content-Length'))          
            while remaining > 0:
                chunk = self.r.read(min(chunk_size, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
        else:
            while True:
                chunk = self.r.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def json(self):
        _content = self.r.read()
        if 'gzip' in self.h.get('Accept-Encoding', '').lower() or 'deflate' in self.h.get('Accept-Encoding', '').lower():
            try:
                buffer = BytesIO(_content)
                gzipper = gzip.GzipFile(fileobj=buffer)
                _content = gzipper.read()
            except:
                try:
                    _content = zlib.decompress(_content)
                except:
                    pass          
        try:
            content_decode = _content.decode()
        except:
            try:
                content_decode = _content.decode('utf-8')
            except:
                content_decode = ''
        try:
            content_json = json_.loads(_content)
        except:
            content_json = {}
        if self.cache_time:
            if content_decode and content_json:
                timestamp = time.time()
                if self.method == 'get':
                    self.c.execute("REPLACE INTO cache_get (url, content, status_code, timestamp) VALUES (?, ?, ?, ?)", (self.url_base64, content_decode, self.r.status, timestamp))
                elif self.method == 'post' and self.payload:
                    self.c.execute("REPLACE INTO cache_post (url, payload, content, status_code, timestamp) VALUES (?, ?, ?, ?, ?)", (self.url_base64, self.payload, content_decode, self.r.status, timestamp))
                self.conn_sqlite.commit()
        self.r.close()
        return content_json        



class HttpResponse_cache:
    def __init__(self, url, status_code, text, content):
        self.url = url
        self.status_code = status_code
        self.text = text
        self.content = content


class req:
    global sleep
    sleep = False

    @classmethod
    def sleep_mode(cls,mode=False):
        global sleep
        sleep = mode

    @classmethod
    def sleep_control(cls):
        random_number = random.randint(3, 6)
        time.sleep(random_number)

    @classmethod
    def headers(cls,url):
        if url.startswith('https://'):
            h = {'Connection': 'keep-alive', 
            'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"', 
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
            }
        else:
            h = {'Connection': 'keep-alive', 
            'sec-ch-ua': '"Microsoft Edge";v="111", "Not(A:Brand";v="8", "Chromium";v="111"', 
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
            }
        return h            

    @classmethod
    def clear_cache(cls):
        if os.path.exists(cache):
            try:
                os.remove(cache)
            except:
                pass
    @classmethod
    def __redirect_get(cls,url,headers={},cookies={},timeout=None,proxy=None,verify=True,replace_headers=False):
        if not url.startswith('https://'):
            if not url.startswith('http://'):
                raise ValueError('Url: Invalid protocol. Only http and https are supported.')
        if proxy:
            if not proxy.startswith('https://'):
                if not proxy.startswith('http://'):
                    raise ValueError('Proxy: Invalid protocol. Only http and https are supported.')
        if replace_headers:
            h = {}
        else:
            h = cls.headers(url)
        if headers:
            h.update(headers)
        parts = urlparse(url)
        scheme_url = parts.scheme
        netloc_url = parts.netloc
        port = parts.port
        if proxy:
            proxy_parse = urlparse(proxy)
            proxy_parts = proxy_parse.netloc.split(":")
            host = proxy_parts[0]
            port = proxy_parts[1]
        else:
            proxy = ''
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
        path = parts.path
        if not path:
            path = '/'
        gets = parts.query
        if gets:
            path = path + '?' + gets 
        if url.startswith('https://'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE            
            if proxy and proxy.startswith('http://') and not proxy.startswith('https://'):
                if port:
                    if timeout:
                        conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host,port=port)
                else:
                    if timeout:
                        conn = http_client.HTTPConnection(host,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host)                
            else:
                if port:
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port)
                else:                
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host)
        else:
            if port:
                if timeout:
                    conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host,port=port)
            else:
                if timeout:
                    conn = http_client.HTTPConnection(host,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host)
        ##### PROXY START #####
        if proxy:
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
            port = parts.port
            try:         
                conn.set_tunnel(host)
            except:
                raise ValueError('Failed to establish tunnel through proxy')
        ##### PROXY END #####
        if cookies:
            cookies_ = []
            for key, value in cookies.items():
                cookies_.append(key + '=' + quote(value))
                h.update({'Cookie': '; '.join(cookies_)})
        conn.request("GET", path, headers=h)
        r = conn.getresponse()
        cookie_dict = {}
        try:
            cookies_temp = r.getheader('Set-Cookie')
            if cookies_temp:
                cookie_obj = http_cookies.SimpleCookie()
                cookie_obj.load(cookies_temp)
                for key, morsel in cookie_obj.items():
                    cookie_dict[key] = morsel.value
        except:
            pass         
        if r.status in [301,302,303,304,307,308]:
            if cookie_dict:
                cookie_redirect = cookie_dict
            elif cookies:
                cookie_redirect = cookies
            else:
                cookie_redirect = {}            
            new_location = r.getheader('Location')
            if new_location:
                if not new_location.startswith('http'):
                    new_location = '%s://%s%s'%(scheme_url,netloc_url,new_location)
                r, new_location = cls.__redirect_get(url=new_location,cookies=cookie_redirect,headers=h,timeout=timeout,proxy=proxy,verify=verify,replace_headers=replace_headers)
            else:
                new_location = url
        else:
            new_location = url
        return r,new_location

    @classmethod
    def __redirect_post(cls,url,data={},json={},headers={},cookies={},timeout=None,proxy=None,verify=True,replace_headers=False):
        if not url.startswith('https://'):
            if not url.startswith('http://'):
                raise ValueError('Url: Invalid protocol. Only http and https are supported.')
        if proxy:
            if not proxy.startswith('https://'):
                if not proxy.startswith('http://'):
                    raise ValueError('Proxy: Invalid protocol. Only http and https are supported.')
        if replace_headers:
            h = {}
        else:
            h = cls.headers(url)
        if headers:
            h.update(headers)
        parts = urlparse(url)
        scheme_url = parts.scheme
        netloc_url = parts.netloc
        port = parts.port
        if proxy:
            proxy_parse = urlparse(proxy)
            proxy_parts = proxy_parse.netloc.split(":")
            host = proxy_parts[0]
            port = proxy_parts[1]
        else:
            proxy = ''
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
        path = parts.path
        if not path:
            path = '/'
        gets = parts.query
        if gets:
            path = path + '?' + gets 
        if url.startswith('https://'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE            
            if proxy and proxy.startswith('http://') and not proxy.startswith('https://'):
                if port:
                    if timeout:
                        conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host,port=port)
                else:
                    if timeout:
                        conn = http_client.HTTPConnection(host,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host)                
            else:
                if port:
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port)
                else:                
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host)
        else:
            if port:
                if timeout:
                    conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host,port=port)
            else:
                if timeout:
                    conn = http_client.HTTPConnection(host,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host)
        ##### PROXY START #####
        if proxy:
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
            port = parts.port
            try:         
                conn.set_tunnel(host)
            except:
                raise ValueError('Failed to establish tunnel through proxy')
        ##### PROXY END #####
        if cookies:
            cookies_ = []
            for key, value in cookies.items():
                cookies_.append(key + '=' + quote(value))
                h.update({'Cookie': '; '.join(cookies_)})
        if data and json:
            raise ValueError('Use data or json argument')                
        if data:
            try:
                payload = urlencode(data)
                h.update({'Content-type': 'application/x-www-form-urlencoded'})
            except:
                payload = data
        elif json:
            payload = json_.dumps(json)
        else:
            raise ValueError('Use data or json arguments')
        conn.request("POST", path, payload, headers=h)
        r = conn.getresponse()
        cookie_dict = {}
        try:
            cookies_temp = r.getheader('Set-Cookie')
            if cookies_temp:
                cookie_obj = http_cookies.SimpleCookie()
                cookie_obj.load(cookies_temp)
                for key, morsel in cookie_obj.items():
                    cookie_dict[key] = morsel.value
        except:
            pass         
        if r.status in [301,302,303,304,307,308]:
            if cookie_dict:
                cookie_redirect = cookie_dict
            elif cookies:
                cookie_redirect = cookies
            else:
                cookie_redirect = {}            
            new_location = r.getheader('Location')
            if new_location:
                if not new_location.startswith('http'):
                    new_location = '%s://%s%s'%(scheme_url,netloc_url,new_location)
                r, new_location = cls.__redirect_post(url=new_location,data=data,json=json,cookies=cookie_redirect,headers=h,timeout=timeout,proxy=proxy,verify=verify,replace_headers=replace_headers)
            else:
                new_location = url
        else:
            new_location = url
        return r,new_location                            

    @classmethod
    def head(cls,url,headers={},cookies={},timeout=None,proxy=None,verify=False,replace_headers=False):
        if not url.startswith('https://'):
            if not url.startswith('http://'):
                raise ValueError('Url: Invalid protocol. Only http and https are supported.')
        if proxy:
            if not proxy.startswith('https://'):
                if not proxy.startswith('http://'):
                    raise ValueError('Proxy: Invalid protocol. Only http and https are supported.')
        if replace_headers:
            h = {}
        else:
            h = cls.headers(url)
        if headers:
            h.update(headers)
        parts = urlparse(url)
        scheme_url = parts.scheme
        netloc_url = parts.netloc
        port = parts.port 
        if proxy:
            proxy_parse = urlparse(proxy)
            proxy_parts = proxy_parse.netloc.split(":")
            host = proxy_parts[0]
            port = proxy_parts[1]
        else:
            proxy = ''
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc 
        path = parts.path           
        if not path:
            path = '/'
        gets = parts.query
        if gets:
            path = path + '?' + gets
        if url.startswith('https://'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            if proxy and proxy.startswith('http://') and not proxy.startswith('https://'):
                if port:
                    if timeout:
                        conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host,port=port)
                else:
                    if timeout:
                        conn = http_client.HTTPConnection(host,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host)                
            else:
                if port:
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port)
                else:                
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host)
        else:
            if port:
                if timeout:
                    conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host,port=port)
            else:
                if timeout:
                    conn = http_client.HTTPConnection(host,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host)
        ##### PROXY START #####
        if proxy:
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
            port = parts.port
            try:         
                conn.set_tunnel(host)
            except:
                raise ValueError('Failed to establish tunnel through proxy')
        ##### PROXY END #####
        if cookies:
            cookies_ = []
            for key, value in cookies.items():
                cookies_.append(key + '=' + quote(value))
                h.update({'Cookie': '; '.join(cookies_)})
        conn.request("HEAD", path, headers=h)
        r = conn.getresponse()
        cookie_dict = {}
        try:
            cookies_temp = r.getheader('Set-Cookie')
            if cookies_temp:
                cookie_obj = http_cookies.SimpleCookie()
                cookie_obj.load(cookies_temp)
                for key, morsel in cookie_obj.items():
                    cookie_dict[key] = morsel.value
        except:
            pass
        url_base64 = None 
        c = None 
        conn_sqlite  = None
        cache_time = None     
        res_http = HttpResponse_http_client(r, url, conn_sqlite, c, h, cache_time,url_base64,cookie_dict,'head',None)
        return res_http                                         



    @classmethod
    def get(cls,url,headers={},cookies={},timeout=None,cache_time=None,proxy=None,verify=True,gzip_encoding=True,replace_headers=False):
        global sleep
        if not url.startswith('https://'):
            if not url.startswith('http://'):
                raise ValueError('Url: Invalid protocol. Only http and https are supported.')
        if proxy:
            if not proxy.startswith('https://'):
                if not proxy.startswith('http://'):
                    raise ValueError('Proxy: Invalid protocol. Only http and https are supported.')
        if replace_headers:
            h = {}
        else:
            h = cls.headers(url)
        if not gzip_encoding and not replace_headers:
            h.pop('Accept-Encoding')
        if headers:
            h.update(headers)
        parts = urlparse(url)
        scheme_url = parts.scheme
        netloc_url = parts.netloc
        port = parts.port
        if proxy:
            proxy_parse = urlparse(proxy)
            proxy_parts = proxy_parse.netloc.split(":")
            host = proxy_parts[0]
            port = proxy_parts[1]
        else:
            proxy = ''
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
        path = parts.path
        if not path:
            path = '/'
        gets = parts.query
        if gets:
            path = path + '?' + gets
        url_base64 = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        if cache_time:
            conn_sqlite = sqlite3.connect(cache)
            c = conn_sqlite.cursor()
            c.execute('''
          CREATE TABLE IF NOT EXISTS cache_get (
              url TEXT PRIMARY KEY,
              content TEXT,
              status_code INTEGER,
              timestamp REAL
          )
          ''')
            c.execute("SELECT content, status_code, timestamp FROM cache_get WHERE url=?", (url_base64,))
            row = c.fetchone()
            if row is not None:
                content, status_code, timestamp = row
                if time.time() - timestamp < cache_time:
                    def cache_json():
                        try:
                            src = content.encode()
                        except:
                            src = content.encode('utf-8')                        
                        try:
                            content_json = json_.loads(src)
                        except:
                            content_json = {}
                        return content_json
                    def cache_content():
                        try:
                            src = content.encode()
                        except:
                            src = content.encode('utf-8')
                        return src
                    def cache_text():
                        return content
                    res_cache = HttpResponse_cache
                    res_cache.content = cache_content()
                    res_cache.text = cache_text()
                    res_cache.json = cache_json()
                    res_cache.status_code = status_code
                    res_cache.url = url                
                    return res_cache
        if sleep:
            cls.sleep_control()
        if url.startswith('https://'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE            
            if proxy and proxy.startswith('http://') and not proxy.startswith('https://'):
                if port:
                    if timeout:
                        conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host,port=port)
                else:
                    if timeout:
                        conn = http_client.HTTPConnection(host,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host)                
            else:
                if port:
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port)
                else:                
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host)
        else:
            if port:
                if timeout:
                    conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host,port=port)
            else:
                if timeout:
                    conn = http_client.HTTPConnection(host,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host)
        ##### PROXY START #####
        if proxy:
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
            port = parts.port
            try:         
                conn.set_tunnel(host)
            except:
                raise ValueError('Failed to establish tunnel through proxy')
        ##### PROXY END #####
        if cookies:
            cookies_ = []
            for key, value in cookies.items():
                cookies_.append(key + '=' + quote(value))
                h.update({'Cookie': '; '.join(cookies_)})
        conn.request("GET", path, headers=h)
        r = conn.getresponse()
        #print(r.getheader("Content-Encoding"))
        ## gzip detector ##
        # gzip = False
        # try:
        #     print('encoding:')
        #     print(r.getheader("Content-Encoding"))
        #     if r.getheader("Content-Encoding") == "gzip":
        #         gzip = True
        # except:
        #     pass
        ###################
        cookie_dict = {}
        try:
            cookies_temp = r.getheader('Set-Cookie')
            if cookies_temp:
                cookie_obj = http_cookies.SimpleCookie()
                cookie_obj.load(cookies_temp)
                for key, morsel in cookie_obj.items():
                    cookie_dict[key] = morsel.value
        except:
            pass        
        if r.status in [301,302,303,304,307,308]:
            if cookie_dict:
                cookie_redirect = cookie_dict
            elif cookies:
                cookie_redirect = cookies
            else:
                cookie_redirect = {}
            new_location = r.getheader('Location')
            if new_location:
                if not new_location.startswith('http'):
                    new_location = '%s://%s%s'%(scheme_url,netloc_url,new_location)
                r, new_location = cls.__redirect_get(url=new_location,cookies=cookie_redirect,headers=h,timeout=timeout,proxy=proxy,verify=verify,replace_headers=replace_headers)
            else:
                new_location = url
        else:
            new_location = url
        if not cookie_dict:
            try:
                cookies_temp = r.getheader('Set-Cookie')
                if cookies_temp:
                    cookie_obj = http_cookies.SimpleCookie()
                    cookie_obj.load(cookies_temp)
                    for key, morsel in cookie_obj.items():
                        cookie_dict[key] = morsel.value
            except:
                pass
        if not cache_time:
            conn_sqlite = None
            c = None
        res_http = HttpResponse_http_client(r, url, conn_sqlite, c, h, cache_time, url_base64, cookie_dict, 'get', None)
        return res_http

    @classmethod
    def post(cls,url,data={},json={},headers={},cookies={},timeout=None,cache_time=None,proxy=None,verify=True,gzip_encoding=True,replace_headers=False):
        global sleep
        if not url.startswith('https://'):
            if not url.startswith('http://'):
                raise ValueError('Url: Invalid protocol. Only http and https are supported.')
        if proxy:
            if not proxy.startswith('https://'):
                if not proxy.startswith('http://'):
                    raise ValueError('Proxy: Invalid protocol. Only http and https are supported.')
        if replace_headers:
            h = {}
        else:
            h = cls.headers(url)
        if not gzip_encoding and not replace_headers:
            h.pop('Accept-Encoding')        
        if headers:
            h.update(headers)
        parts = urlparse(url)
        scheme_url = parts.scheme
        netloc_url = parts.netloc
        port = parts.port
        if proxy:
            proxy_parse = urlparse(proxy)
            proxy_parts = proxy_parse.netloc.split(":")
            host = proxy_parts[0]
            port = proxy_parts[1]
        else:
            proxy = ''
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
        path = parts.path
        if not path:
            path = '/'
        gets = parts.query
        if gets:
            path = path + '?' + gets
        if data and json:
            raise ValueError('Use data or json argument')
        if data:
            try:
                payload = urlencode(data)
                h.update({'Content-type': 'application/x-www-form-urlencoded'})
            except:
                payload = data
        elif json:
            payload = json_.dumps(json)
            h.update({'Content-type': 'application/json'})
        else:
            raise ValueError('Use data or json arguments')            
        url_base64 = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        if cache_time:
            conn_sqlite = sqlite3.connect(cache)
            c = conn_sqlite.cursor()
            c.execute('''
          CREATE TABLE IF NOT EXISTS cache_post (
              url TEXT PRIMARY KEY,
              payload TEXT,
              content TEXT,
              status_code INTEGER,
              timestamp REAL
          )
          ''')
            c.execute("SELECT content, status_code, timestamp FROM cache_post WHERE url=? and payload=?", (url_base64,payload))
            row = c.fetchone()
            if row is not None:
                content, status_code, timestamp = row
                if time.time() - timestamp < cache_time:
                    def cache_json():
                        try:
                            src = content.encode()
                        except:
                            src = content.encode('utf-8')
                        try:
                            content_json = json_.loads(src)
                        except:
                            content_json = {}
                        return content_json
                    def cache_content():
                        try:
                            src = content.encode()
                        except:
                            src = content.encode('utf-8')
                        return src
                    def cache_text():
                        return content
                    res_cache = HttpResponse_cache
                    res_cache.content = cache_content()
                    res_cache.text = cache_text()
                    res_cache.json = cache_json()
                    res_cache.status_code = status_code
                    res_cache.url = url                
                    return res_cache
        if sleep:
            cls.sleep_control()           
        if url.startswith('https://'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE            
            if proxy and proxy.startswith('http://') and not proxy.startswith('https://'):
                if port:
                    if timeout:
                        conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host,port=port)
                else:
                    if timeout:
                        conn = http_client.HTTPConnection(host,timeout=timeout)
                    else:
                        conn = http_client.HTTPConnection(host)                
            else:
                if port:
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,port=port,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,port=port)
                else:                
                    if timeout:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,timeout=timeout,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host,timeout=timeout)
                    else:
                        if not verify:
                            conn = http_client.HTTPSConnection(host,context=context)
                        else:
                            conn = http_client.HTTPSConnection(host)
        else:
            if port:
                if timeout:
                    conn = http_client.HTTPConnection(host,port=port,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host,port=port)
            else:
                if timeout:
                    conn = http_client.HTTPConnection(host,timeout=timeout)
                else:
                    conn = http_client.HTTPConnection(host)
        ##### PROXY START #####
        if proxy:
            try:
                host = parts.netloc.split(":")[0]
            except:
                host = parts.netloc
            port = parts.port
            try:         
                conn.set_tunnel(host)
            except:
                raise ValueError('Failed to establish tunnel through proxy')
        ##### PROXY END #####
        if cookies:
            cookies_ = []
            for key, value in cookies.items():
                cookies_.append(key + '=' + quote(value))
                h.update({'Cookie': '; '.join(cookies_)})
        if data:
            try:
                payload = urlencode(data)
            except:
                payload = data
        elif json:
            payload = json_.dumps(json)
        else:
            raise ValueError('Use data or json arguments')
        conn.request("POST", path, payload, headers=h)
        r = conn.getresponse()
        cookie_dict = {}
        try:
            cookies_temp = r.getheader('Set-Cookie')
            if cookies_temp:
                cookie_obj = http_cookies.SimpleCookie()
                cookie_obj.load(cookies_temp)
                for key, morsel in cookie_obj.items():
                    cookie_dict[key] = morsel.value
        except:
            pass
        if r.status in [301,302,303,304,307,308]:
            if cookie_dict:
                cookie_redirect = cookie_dict
            elif cookies:
                cookie_redirect = cookies
            else:
                cookie_redirect = {}
            new_location = r.getheader('Location')
            if new_location:
                if not new_location.startswith('http'):
                    new_location = '%s://%s%s'%(scheme_url,netloc_url,new_location)
                r, new_location = cls.__redirect_post(url=new_location,data=data,json=json,cookies=cookie_redirect,headers=h,timeout=timeout,proxy=proxy,verify=verify,replace_headers=replace_headers)
            else:
                new_location = url
        else:
            new_location = url
        if not cookie_dict:
            try:
                cookies_temp = r.getheader('Set-Cookie')
                if cookies_temp:
                    cookie_obj = http_cookies.SimpleCookie()
                    cookie_obj.load(cookies_temp)
                    for key, morsel in cookie_obj.items():
                        cookie_dict[key] = morsel.value
            except:
                pass
        if not cache_time:
            conn_sqlite = None
            c = None            
        res_http = HttpResponse_http_client(r, url, conn_sqlite, c, h, cache_time, url_base64, cookie_dict, 'post', payload)
        return res_http                       
