
   import hmac, hashlib, datetime, requests, os, pandas as pd

def generate_hmac(method, url, secret_key, access_key):
    path, _, query = url.partition('?')
    datetime_str = datetime.datetime.utcnow().strftime('%y%m%dT%H%M%SZ')
    message = datetime_str + method + path + query
    signature = hmac.new(bytes(secret_key, 'utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime_str}, signature={signature}"

def main():
    # Load keys from Secrets
    ACCESS_KEY = os.environ['ACCESS_KEY']
    SECRET_KEY = os.environ['SECRET_KEY']
    
    # Category: Consumer Electronics (가전디지털: 1016)
    URL = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/bestcategories/1016"
    auth = generate_hmac("GET", URL, SECRET_KEY, ACCESS_KEY)
    
    res = requests.get(f"https://api-gateway.coupang.com{URL}", headers={"Authorization": auth, "Content-Type": "application/json"})
    
    if res.status_code == 200:
        products = res.json().get('data', [])[:20]
        
        # Clean Data & Shorten Links
        rows = []
        for p in products:
            rows.append({
                '상품명': p['productName'],
                '가격': p['productPrice'],
                # This part shortens the long URL into "클릭해서 이동"
                '링크': f'=HYPERLINK("{p["productUrl"]}", "클릭해서 이동")'
            })
            
        df = pd.DataFrame(rows)
        filename = f"Coupang_Top20_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx"
        
        # Save to Excel
        df.to_excel(filename, index=False)
        print(f"Successfully created: {filename}")

if __name__ == "__main__":
    main()
