import requests
from bs4 import BeautifulSoup
import json

def get_txt_from_url(request):
    try:
        # ページのコンテンツをフェッチ
        url = request.args.get('url')
        page = requests.get(url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')

        # タイトルを抽出
        title = soup.title.string if soup.title else "Untitled"
        markdown_output = f"# {title}\n"

        # 主要なテキストを抽出
        for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if p.name == 'h1':
                markdown_output += f"# {p.get_text()}\n"
            elif p.name == 'h2':
                markdown_output += f"## {p.get_text()}\n"
            elif p.name.startswith('h'):
                markdown_output += f"### {p.get_text()}\n"
            else:
                markdown_output += f"{p.get_text()}\n\n"

        # JSON形式で出力
        output_json = json.dumps({"url": url, "content": markdown_output}, ensure_ascii=False)
        
        # CORS許可の設定
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        
        return (output_json, 200, headers)

    except Exception as e:
        error_json = json.dumps({"error": str(e)})
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        return (error_json, 500, headers)