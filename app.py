import datetime
from flask import Flask, request
from werkzeug.contrib.atom import AtomFeed
from radiorus import radiorus_podcast

app = Flask(__name__)
@app.route('/podcast/<podcast_id>')
def rss_feed(podcast_id):
    podcast = None
    try:

        # Cчитываем информацию об эпизодах из БД:
        podcast = radiorus_podcast(podcast_id) # 57260 'Как курица лапой'

        # Формируем ленту:
        feed = AtomFeed(
            podcast.title, 
            feed_url=request.url, 
            url=podcast.base_url,
            logo=podcast.logo_url
        )

        for episode in podcast.episodes:

            links = []
            for audio_record in episode['audio_records']:
                link = {
                    "rel": "enclosure",
                    "type": "audio/mpeg",
                    "href": audio_record['url'],
                    "length": audio_record['length'],
                    "title": audio_record['title'],
                    }
                links.append(link)

            published = episode['published']
            feed.add(
                title=episode['title'], 
                content=episode['description'],
                content_type='text',
                author="Радио России",
                icon=episode['image_url'],
                url=episode['url'],
                links=links,
                updated=published,
                published=published)

        # Отдаём ленту
        return feed.get_response()

    except Exception as error:
        # TODO: Добавить нормальный обработчик ошибок
        pass

    finally:
        if podcast is not None:
            del podcast
