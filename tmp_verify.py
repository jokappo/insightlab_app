import requests 
paths=['/tickers','/processed/AAPL','/predictions/latest','/alerts/AAPL'] 
for p in paths: 
    r=requests.get('http://localhost:8000'+p, timeout=10) 
    print(p, r.status_code, r.text[:180]) 
