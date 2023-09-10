import requests
from bs4 import BeautifulSoup
import json

def get_txt_from_url(request):
    try:
        # ページのコンテンツをフェッチ
        url = request.args.get('url')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76', 'Referer': 'https://search.yahoo.co.jp/realtime/'}
        page = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')

        # タイトルを抽出
        title = soup.title.string if soup.title else "Untitled"
        markdown_output = f"# {title}\n"

        outputted_texts = set()

        # 主要なテキストを抽出
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'li', 'table']):
            text = tag.get_text().strip()

            # 親が<li>タグであればスキップ
            if tag.find_parent("li"):
                continue

            if text in outputted_texts:
                continue

            outputted_texts.add(text)
            
            if tag.name == 'h1':
                markdown_output += f"# {tag.get_text().strip()}\n"
            elif tag.name == 'h2':
                markdown_output += f"## {tag.get_text().strip()}\n"
            elif tag.name.startswith('h'):
                markdown_output += f"### {tag.get_text().strip()}\n"
            elif tag.name == 'pre':
                markdown_output += f"```\n{tag.get_text().strip()}\n```\n"
            elif tag.name == 'li':
                markdown_output += f"- {tag.get_text().strip()}\n"
            elif tag.name == 'table':
                rows = tag.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text().strip() for cell in cells]
                    markdown_output += "|".join(cell_texts) + "\n"
                    if cells and all(cell.name == 'th' for cell in cells):
                        markdown_output += "|".join(["---" for _ in cells]) + "\n"
            else:
                markdown_output += f"\n{tag.get_text().strip()}\n\n"

        # JSON形式で出力
        output_json = json.dumps({"url": url, "content": markdown_output}, ensure_ascii=False)
        
        # CORS許可の設定
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        
        return (output_json, 200, headers)

    except requests.exceptions.RequestException as e:
        print(f"Requests exception occurred: {e}")
        error_json = json.dumps({"error": str(e)})
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        return (error_json, 500, headers)
    except Exception as e:
        print(f"General exception occurred: {e}")
        error_json = json.dumps({"error": str(e)})
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        return (error_json, 500, headers)
