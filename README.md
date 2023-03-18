# fasthttp

fasthttp é uma ferramenta de acesso a sites usando http.client do python de baixo nivel e com maior privacidade e velocidade, isso por que http.client usa socket por baixo que é escrito em c e pelo fato de http.client dificultar analises de programas como fiddler e wireshark.

por padrão o metodo get e post possui redirecionamento ativado

## Instalação
```bash
pip install git+https://github.com/zoreu/fasthttp
```

## modo sleep
```python
# caso queira que o acesso seja o mais proximo do usuario normal
# existe o modo sleep pra adicionar uma pausa antes de cada acesso
from fasthttp import req
req.sleep_mode(True)
```

## post
```python
# por padrão o fasthttp usa headers de navegador de pc
from fasthttp import req
r = req.post('https://httpbin.org/post',headers={'Referer': 'https://sitelouco.com/'},data={'nome': 'chuck', 'sobrenome': 'norris'})
print(r.json())
```

## head
```python
r = req.head('https://httpbin.org/ip')
print(r.status_code)
```


## get
```python
r = req.get('https://httpbin.org/ip')
print(r.text)
```

## modo cache
```python
# cache com 300 segundos, onde a cada 300 segundos é renovado o cache
r = req.get('https://httpbin.org/ip',cache_time=200)
print(r.text)
```

## limpando cache
```python
# para apagar o cache use a função clear_cache
req.clear_cache()
```

## proxy
```python
# observação: o proxy é usado tanto pra site http como pra site https
r = req.get('https://httpbin.org/ip',proxy='http://127.0.0.1:8888')
print(r.text)

