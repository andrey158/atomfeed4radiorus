import re
import datetime
from requests_html import HTMLSession
import psycopg2
import psycopg2.extras
from config import config

#
# Получение даты из строки
#  
def get_date(date_string):
    month2num = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12
    }

    date_list = date_string.split()
    day = int(date_list[0])
    month = month2num[date_list[1].lower()]
    year = int(date_list[2])

    return datetime.date(year, month, day)

class radiorus_podcast:
    db_connection = None
    db_podcasts_cursor = None
    db_episodes_cursor  = None
    db_audio_records_cursor = None

    def __init__(self, podcast_id):
        if podcast_id.isdigit() == False:
            # TODO: Добавить нормальный Exception
            raise Exception('')

        self.podcast_id = podcast_id
        self.base_url = 'http://www.radiorus.ru/brand/audio/id/{}/page/'.format(self.podcast_id)

        params = config()
        self.db_connection = psycopg2.connect(**params)
        self.db_podcasts_cursor = self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.db_episodes_cursor = self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.db_audio_records_cursor = self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if self.get_podcast_info() == False:
            self.update_db()

        self.episodes = self.get_episodes()
        
    def __del__(self):
        if self.db_connection is not None:
            self.db_connection.commit()
            self.db_podcasts_cursor.close()
            self.db_episodes_cursor.close()
            self.db_audio_records_cursor.close()
            self.db_connection.close()

    def get_podcast_info(self):
        self.db_podcasts_cursor.execute("SELECT * FROM podcasts WHERE id = %s", (self.podcast_id,))
        podcast = self.db_podcasts_cursor.fetchone()
        if podcast is not None:
            self.title = podcast['title']
            self.logo_url = podcast['logo_url']
            return True            
        else:
            self.title = ""
            self.logo_url = ""
            return False
#
#   Парсинг информации об эпизоде и сохранение информации в БД
#
    def process_episode(self, episode):
        # Заголовок эпизода
        title = episode.find('h3', first=True).text

        # Картинка эпизода
        try:
            image_url = episode.find('div.img-container-audio img', first=True).attrs['src']
        except Exception as error:
            image_url = ""

        # Краткое описание эпизода
        description = episode.find('.text', first=True).text

        # Ссылка на эпизод
        episode_info = episode.find('.br-info > a', first=True)
        for link in episode_info.absolute_links:
            episode_url = link

        episode_id = re.search('(\d+)\/$', episode_url)[1]

        # Дата выхода эпизода:
        date = episode.find('p.date', first=True).text
        if date == "": 
            return True

        published = get_date(date)

        # Пишем в БД:
        try:
            self.db_episodes_cursor.execute("INSERT INTO episodes VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                (
                    int(self.podcast_id),   # podcast_id    - id подкаста
                    int(episode_id),        # id            - id эпизода
                    title,                  # title         - заголовок эпизода
                    description,            # description   - краткое описание эпизода
                    episode_url,            # url           - URL эпизода
                    image_url,              # image_url     - URL картинки эпизода
                    published              # published     - дата публикации эпизода
                )
            )

        except (Exception, psycopg2.DatabaseError) as error:
            return False        # Сообщаем, что дальше обрабатывать не надо (такой эпизод уже есть в БД)

        # Аудио-дорожки эпизода:
        audio_records = episode.find('div.audio-block')
        audio_subrecords = episode.find('div.track') # запрос для "вложенных" дорожек
        if audio_subrecords !=[]:
            audio_records.extend(audio_subrecords)    

        for audio_record in audio_records:
            try:
                audio_info = audio_record.find('div.br-audio', first=True)

                audio_record_title = audio_record.find('h3', first=True).text 
                audio_record_url = audio_info.attrs['data-url']
                audio_record_id = re.search('\d+$', audio_record_url)[0]
                audio_record_length = audio_info.find('span.br-duration', first=True).text

            except Exception as error:
                audio_record_url = ""
                audio_record_length = ""
                audio_record_id = 0

            # Пишем в БД:
            if audio_record_id != 0:
                try:
                    self.db_audio_records_cursor.execute("INSERT INTO audio_records VALUES (%s, %s, %s, %s, %s, %s)", 
                        (
                            int(self.podcast_id),   # podcast_id    - id подкаста
                            int(episode_id),        # episode_id    - id эпизода
                            int(audio_record_id),   # id            - id аудио-записи
                            audio_record_title,     # title         - заголовок аудио-записи
                            audio_record_url,       # url           - URL аудио-записи
                            audio_record_length     # length        - продолжительность
                        )
                    )
                except (Exception, psycopg2.DatabaseError) as error:
                    continue
        
        return True

#
#  Обработка страницы
#
    def process_page(self, page_num):
        episodes = self.http_request.html.find('div.audio-element-list div.item')

        # Обработка списка эпизодов для каждой страницы:
        for episode in episodes:
            if self.process_episode(episode) == False:
                return False    # Сообщаем, что дальше обрабатывать не надо

        return True

# 
# Запись в БД информации об эпизодах 
#
    def update_db(self, only_podcasts=False):
        self.http_request = HTMLSession().get(self.base_url)
        if self.http_request.status_code != 200:
            # TODO: Добавить нормальный Exception
            raise Exception('')

        h1 = self.http_request.html.find('h1', first=True)
        self.title = h1.element.text.strip()
        self.logo_url = self.http_request.html.find('div.person > img', first=True).attrs['src']

        try:
            self.db_podcasts_cursor.execute("INSERT INTO podcasts VALUES (%s, %s, %s)", 
                (
                    int(self.podcast_id),
                    self.title,
                    self.logo_url
                )
            )

        except (Exception, psycopg2.DatabaseError) as error:
            pass

        if only_podcasts == True: return

        # Анализируем количество страниц в списке:
        paginator = self.http_request.html.find('.paginator', first=True)

        min_page = 1
        max_page = 1
        for page_link in paginator.links:
            page_num = int(re.search('\d+$', page_link)[0])
            if page_num > max_page : max_page = page_num

        page_num = 1
        while page_num <= max_page:
            # Обрабатываем страницу с номером page_num
            if self.process_page(page_num) == False: 
                break

            # Переходим к следующей странице
            page_num = page_num + 1
                
            if page_num > max_page: continue

            url = self.base_url + str(page_num)
            self.http_request = HTMLSession().get(url)         

#
# Получение из БД информации об эпизодах подкаста
#
    def get_episodes(self):
        episodes=[]
        try:
            self.db_episodes_cursor.execute("SELECT * FROM episodes WHERE podcast_id = %s", (self.podcast_id,))
            row = self.db_episodes_cursor.fetchone()
 
            while row is not None:

                episode = {'audio_records': []}
                episode.update(row)

                self.db_audio_records_cursor.execute("SELECT * FROM audio_records WHERE podcast_id = %s AND episode_id = %s", (episode['podcast_id'], episode['id'],))
                audio_records = self.db_audio_records_cursor.fetchall()
                episode['audio_records'] = audio_records

                episodes.append(episode)
                row = self.db_episodes_cursor.fetchone()

            return episodes
        except (Exception, psycopg2.DatabaseError) as error:
            return []