import requests
import json

def call_get_txt_from_url(target_url):
    endpoint = "https://asia-northeast2-my-pj-20230703.cloudfunctions.net/get_txt_from_url"
    params = {"url": target_url}
    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = json.loads(response.text)
        return data['content']
    else:
        return f"Error: {response.status_code}, {response.text}"

# 例としてのWebページのURLをここに入れる
target_url = "https://qiita.com/qiitadaisuki/items/2160a390ce91283707a1"
result = call_get_txt_from_url(target_url)
print(result)

# 【実行例】
# > python .\test.py