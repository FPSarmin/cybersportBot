import requests
import pandas
from tqdm import tqdm
from pandas import DataFrame
from bs4 import BeautifulSoup


class News:
    def __init__(self, df: pandas.DataFrame):
        self.df = df

    @staticmethod
    def from_csv_file(csv_path: str):
        return News(
            pandas.read_csv(csv_path)
        )

    @staticmethod
    def create_empty_db():
        df = pandas.DataFrame(
            {
                'news_title': [],
                'news_link': [],
                'news_type': [],
                'news_description': [],
                'new': []
            }
        )
        df.to_csv('users_db.csv', encoding='utf-8', index=False)
        return News.from_csv_file('users_db.csv')

    def update(self):
        response = requests.get('https://www.cybersport.ru/news').content
        soup = BeautifulSoup(response, 'html.parser')
        new = False
        try:
            news_list = soup('ul', 'cs-news__list list-unstyled sys-content-list')[0]('li',
                                                                                      'cs-news__item icon-game--colour')
            for n in tqdm(news_list):
                title = n.a.text
                link = 'https://www.cybersport.ru' + n.a['href']
                tp = n.g['class'][0].replace('icon-game--', '')
                if self.df.empty or len(self.df[self.df.news_link == link]) == 0 and \
                        link.find('https://t.me/csru_official') == -1:
                    new = True
                    little_soup = BeautifulSoup(
                        requests.get(link).content, 'html.parser')
                    try:
                        short_descriptions = little_soup('div', 'typography js-mediator-article')[0]\
                            .p.text.replace('\xa0', ' ')
                    except BaseException:
                        short_descriptions = "Нет короткого описания"
                    self.df = self.df.append({
                        'news_title': title,
                        'news_link': link,
                        'news_type': tp,
                        'news_description': short_descriptions,
                        'new': 1
                    }, ignore_index=True)
            self.df.to_csv("news_db.csv", encoding='utf-8', index=False)
        except BaseException:
            pass
        return new

    def sample(self, types: list):
        df = self.df.apply(
            lambda row: row['news_type'] in types,
            axis=1
        )
        df = self.df[df]
        return df.sample(1)

    def change_news_status(self, link):
        self.df.loc[self.df[self.df.news_link == link].index, 'new'] = 0


try:
    news = News.from_csv_file('news_db.csv')
except BaseException:
    news = News.create_empty_db()
