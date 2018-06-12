# -*- coding: utf-8 -*-
"""
Spyder Editor

"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

class NewsFetcher:
    def __init__(self):
        print("New Object Created!")
    def getSources(self):
        source_url = 'https://newsapi.org/v1/sources?language=en'
        response = requests.get(source_url).json()
        sources = []
        for source in response['sources']:
            sources.append(source['id'])
        return sources
    
    def mapping(self):
        d = {}
        response = requests.get('https://newsapi.org/v1/sources?language=en')
        response = response.json()
        for s in response['sources']:
            d[s['id']] = s['category']
        return d
    
    def category(self,source, m):
        try:
            return m[source]
        except:
            return 'NC'
    
    def getDailyNews(self):
        sources = self.getSources()
        key = '57dfa3b34bcf43ffa8cdce89cc139d85'
        url = 'https://newsapi.org/v1/articles?source={0}&sortBy={1}&apiKey={2}'
        responses = []
        for i,source in enumerate(sources):
            
            try:
                u = url.format(source, 'top', key)
            except:
                u = url.format(source, 'latest', key)
            
            response = requests.get(u)
            r = response.json()
            
            try:
                for article in r['articles']:
                    article['source'] = source
                responses.append(r)
            except:
                print('Rate limit exceeded ... please wait and retry in 6 hours')
                print(r)
                return None
                    
        articles = list(map(lambda r: r['articles'], responses))
        articles = list(reduce(lambda x,y: x+y, articles))
        
        news = pd.DataFrame(articles)
        news = news.dropna()
        news = news.drop_duplicates()
        news.reset_index(inplace=True, drop=True)
        print(news.head())
        d = self.mapping()
        news['category'] = news['source'].map(lambda s: self.category(s, d))
        news['scraping_date'] = datetime.now()
    
        try:
            aux = pd.read_csv('./data/news.csv')
            aux = aux.append(news)
            aux = aux.drop_duplicates('url')
            aux.reset_index(inplace=True, drop=True)
            aux.to_csv('./data/news.csv', encoding='utf-8', index=False)
        except:
            news.to_csv('./data/news.csv', index=False, encoding='utf-8')
            
        print('Done')

