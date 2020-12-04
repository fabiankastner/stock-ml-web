import http.client

conn = http.client.HTTPSConnection("alpha-vantage.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "cb53b74ad7mshd96157672a5da7fp171cd0jsnfae25e94c672",
    'x-rapidapi-host': "alpha-vantage.p.rapidapi.com"
    }

conn.request("GET", "/query?function=GLOBAL_QUOTE&symbol=TSLA", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))