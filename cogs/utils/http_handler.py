from urllib.request import Request, urlopen

class HTTPHandler:
    def __init__(self):
        pass
    
    def get(self, url, headers):
        if not headers:
            headers = dict()
        request = Request(url, headers = headers)
        response = urlopen(request)
        return response
    
    def post(self, url, headers, data):
        if not headers:
            headers = dict()
        request = Request(url, headers = headers)
        response = urlopen(request, data=data.encode("utf-8"))
        return response