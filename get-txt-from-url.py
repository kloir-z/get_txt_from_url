import requests
from bs4 import BeautifulSoup
import json

def get_txt_from_url(url):
    try:
        # ページのコンテンツをフェッチ
        page = requests.get(url)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')

        # タイトルを抽出
        title = soup.title.string if soup.title else "Untitled"
        markdown_output = f"# {title}\n"

        # 主要なテキストを抽出
        for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if p.name.startswith('h'):
                markdown_output += f"{p.name} {p.get_text()}\n"
            else:
                markdown_output += f"{p.get_text()}\n\n"

        # JSON形式で出力
        output_json = json.dumps({"url": url, "content": markdown_output}, ensure_ascii=False)
        return output_json

    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    url = "https://www.nature.com/articles/s41467-023-40942-2"  # 置き換えてください
    print(get_txt_from_url(url))