#!/usr/bin/env python3
# admin.py
# author: Sébastien Combéfis, Mathilde Becquereau & Martin Degeldt
# version: December 22, 2016

import json
from urllib.request import urlopen

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout


def loaddata():
    data = urlopen('http://localhost:8080/getcomments').read()
    data = json.loads(data.decode('utf-8'))
    reported = [e for e in data['comments'] if e['report']]
    titles = []
    for i in range(len(reported)):
        titles.append('{} - {}'.format(i+1, reported[i]['pseudo']))
    return reported, titles


class SupaHeroForm(GridLayout):
    reported, heros = loaddata()
    reported_spr = ObjectProperty()
    detail_txt = ObjectProperty()
    i = -1

    def showdetail(self, text):
        if text != '':
            self.i = int(text.split('-')[0].strip())-1
            comment = self.reported[self.i]
            self.detail_txt.text = '''- Univers: {}
    - Héro: {}
    - Commentaire: {}'''.format(comment['univers'],
                                comment['name'],
                                comment['text'])

    def delete(self):
        data = urlopen('http://localhost:8080/deletecom?idee={}'.format(self.reported[self.i]['id']))
        data = data.read().decode('utf8')
        if data == 'OK':
            self.detail_txt.text = ''
            self.reported_spr.text = ''
            self.reported, self.reported_spr.values = loaddata()

    def commentok(self):
        data = urlopen('http://localhost:8080/commentok?idee={}'.format(self.reported[self.i]['id']))
        data = data.read().decode('utf8')
        if data == 'OK':
            self.detail_txt.text = ''
            self.reported_spr.text = ''
            self.reported, self.reported_spr.values = loaddata()


class SupaHeroApp(App):
    title = 'Supa Hero'


SupaHeroApp().run()
