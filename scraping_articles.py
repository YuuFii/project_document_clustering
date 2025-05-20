import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import argparse

category_mapping = {
    'olahraga': 7,
    'ekonomi': 5,
    'nasional': 3,
    'internasional': 6,
    'teknologi': 8,
    'otomotif': 577
}

def scrape_category(category_name, category_code, page_number):
    url = f"https://www.cnnindonesia.com/{category_name}/indeks/{category_code}?page={page_number}"
    print(f"Scraping: {url}")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []

    for item in soup.select('article'):
        title_tag = item.find('h2')
        link_tag = item.find('a')

        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)
            link = link_tag['href']
            
            articles.append({
                'title': title,
                'link': link,
                'category': category_name
            })

    return articles

def scrape_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        date_tag = soup.select_one('.text-cnn_grey text-sm')
        date = date_tag.get_text(strip=True) if date_tag else ''

        content_paragraphs = soup.select('.detail-text p')
        content = '\n'.join([p.get_text(strip=True) for p in content_paragraphs])

        return {
            'content': content,
            'date': date
        }
    except Exception as e:
        print(f"Error saat scrape artikel {url}: {e}")
        return {
            'content': '',
            'date': ''
        }

def main():
    parser = argparse.ArgumentParser(description='CNN Indonesia Scraper')
    parser.add_argument('--max_pages', type=int, default=5,
                        help='Jumlah maksimal halaman per kategori (default: 5)')
    args = parser.parse_args()

    all_articles = []

    for category_name, category_code in category_mapping.items():
        print(f"\n[+] Scraping kategori: {category_name}")
        for page in range(1, args.max_pages + 1):
            try:
                articles = scrape_category(category_name, category_code, page)
                for article in articles:
                    print(f"  - Mengambil konten: {article['title']}")
                    content_data = scrape_article_content(article['link'])
                    article.update(content_data)
                    all_articles.append(article)
                time.sleep(1)
            except Exception as e:
                print(f"Error pada halaman {page} kategori {category_name}: {e}")

    # Simpan ke CSV
    df = pd.DataFrame(all_articles)
    output_file = f"cnn_indonesia_berita_{args.max_pages}_pages.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Scraping selesai! Data disimpan ke {output_file}")


if __name__ == "__main__":
    main()