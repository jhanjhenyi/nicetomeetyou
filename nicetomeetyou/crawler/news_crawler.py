import os
import sys

from django.core.wsgi import get_wsgi_application

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nicetomeetyou.settings')
sys.path.append(PROJECT_DIR)

application = get_wsgi_application()

from requests_html import HTMLSession, HTML

from news.models import *

session = HTMLSession()


def get_news(pages: int = 10):

    url_base = "https://nba.udn.com/"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
    }
    
    def get_news_url_list(pages: int) -> list:
        '''Gets all news url'''

        url_news = "/nba/news"
        r = session.get(url=url_base + url_news, headers=headers)
        
        links = []
        while pages > 0:
            html = HTML(html=r.text)
            news_list_body = html.find('#news_list_body', first=True)
            links.extend(list(news_list_body.links))

            page_link_next = html.find(
                'div > gonext > a[data-id=right]', first=True).attrs['href']

            r = session.get(url=url_base + page_link_next, headers=headers)
            pages += -1

        return links

    news_url_list = get_news_url_list(pages)

    post_list = []
    for url in news_url_list:
        post_id = url.split("/")[-1]

        try:
            if Post.objects.filter(id=post_id).exists():
                continue

            post_source_url = url_base + url

            r = session.get(url=post_source_url, headers=headers)
            html = HTML(html=r.text)

            story_body_content = html.find('#story_body_content', first=True)

            post_title = story_body_content.find(
                'h1.story_art_title', first=True).text
            post_image_url = story_body_content.find(
                'figure.photo_center > a > img', first=True).attrs['data-src']

            post_content = ""
            for p in story_body_content.find('span > p')[1:]:
                post_content += str(p.text)

            post_list.append(Post(
                id=post_id,
                title=post_title,
                content=post_content,
                image_url=post_image_url,
                source_url=post_source_url
            ))
            print(f"{post_id} {post_title} ok.")
        except:
            continue

    Post.objects.bulk_create(post_list)
    print("Save Completed.")

if __name__ == "__main__":
    print("-----Crawler Start-----")
    get_news()
    print("-----Crawler End-----")
