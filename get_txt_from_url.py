import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import re

def get_txt_from_url(request):
    try:
        url = request.args.get('url')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76',
            'Referer': 'https://search.yahoo.co.jp/realtime/'
        }
        
        markdown_output_list = []  # ページごとの内容を格納する配列
        current_url = url

        while current_url:
            page = requests.get(current_url, headers=headers, verify=False)
            soup = BeautifulSoup(page.content, 'html.parser')

            # ここで各ページからテキストを抽出（詳細は後述）
            markdown_output_list.append(extract_content(soup))
            
            # 次のページのリンクを見つける
            next_page_tag = None
            for a_tag in soup.find_all('a', href=True):
                if re.search(r'次.*ページ|next.*page', a_tag.get_text(), re.IGNORECASE):
                    next_page_tag = a_tag
                    break
                    
            if next_page_tag:
                current_url = next_page_tag.get('href')
                current_url = urljoin(url, current_url)  # 相対パスを絶対URLに変換
            else:
                current_url = None

        output_json = json.dumps({"url": url, "content": markdown_output_list}, ensure_ascii=False)
        
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        
        return (output_json, 200, headers)

    except requests.exceptions.RequestException as e:
        print(f"Requests exception occurred: {e}, Exception Type: {e.__class__.__name__}")
        error_json = json.dumps({"error": str(e)})
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        return (error_json, 500, headers)
    except Exception as e:
        print(f"General exception occurred: {e}, Exception Type: {e.__class__.__name__}")
        error_json = json.dumps({"error": str(e)})
        headers = {
            'Access-Control-Allow-Origin': '*'
        }
        return (error_json, 500, headers)

def extract_content(soup):
    # タイトルを抽出
    title = soup.title.string if soup.title else "Untitled"
    markdown_output = f"# {title}\n"

    outputted_texts = set()

    # 主要なテキストを抽出
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'li', 'table', 'strong', 'ol']):
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
            pre_text = tag.get_text()
            pre_text = pre_text.replace('\\n', '\n')
            markdown_output += f"```\n{pre_text}\n```\n"
        elif tag.name == 'ol':
            for i, li_tag in enumerate(tag.find_all('li'), 1):
                markdown_output += f"{i}. {li_tag.get_text().strip()}\n"
        elif tag.name == 'li':
            # 親が<ol>タグであればスキップ（既に処理済み）
            if tag.find_parent("ol"):
                continue
            markdown_output += f"- {tag.get_text().strip()}\n"
        elif tag.name == 'table':
            rows = tag.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text().strip() for cell in cells]
                markdown_output += "|".join(cell_texts) + "\n"
                if cells and all(cell.name == 'th' for cell in cells):
                    markdown_output += "|".join(["---" for _ in cells]) + "\n"
        elif tag.name == 'strong' or tag.name == 'b':
            markdown_output += f"**{tag.get_text().strip()}**\n"
        else:
            markdown_output += f"\n{tag.get_text().strip()}\n\n"

    return markdown_output
