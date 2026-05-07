import hmac, hashlib, datetime, requests, os, pandas as pd

def generate_hmac(method, url, secret_key, access_key):
    path, _, query = url.partition('?')
    datetime_str = datetime.datetime.utcnow().strftime('%y%m%dT%H%M%SZ')
    message = datetime_str + method + path + query
    signature = hmac.new(bytes(secret_key, 'utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime_str}, signature={signature}"

def main():
    ACCESS_KEY = os.environ['ACCESS_KEY']
    SECRET_KEY = os.environ['SECRET_KEY']
    
    # 가전디지털 카테고리(1016) 기준
    URL = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/bestcategories/1016"
    auth = generate_hmac("GET", URL, SECRET_KEY, ACCESS_KEY)
    
    res = requests.get(f"https://api-gateway.coupang.com{URL}", headers={"Authorization": auth, "Content-Type": "application/json"})
    
    if res.status_code == 200:
        products = res.json().get('data', [])[:20]
        df = pd.DataFrame(products)[['productName', 'productPrice', 'productUrl']]
        filename = f"Coupang_Top20_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"{filename} 파일 생성 완료!")

if __name__ == "__main__":
    main()
