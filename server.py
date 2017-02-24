#!/usr/bin/env python3
# server.py
# author: Mathilde Becquereau & Martin Degeldt
# version: December 22, 2016

import json
import os.path

import codecs

import cherrypy
import jinja2

import jinja2plugin
import jinja2tool


class SupaHero:
    """Website of super hero's reference."""
    def __init__(self):
        self.info = self.loadinfo()
        self.hero = self.info['heros']
        self.comments = self.info['comments']

    def count(self):
        if len(self.comments) == 0:
            return 0
        return self.comments[-1]['id']

    @cherrypy.expose
    def index(self):
        """Home page of the website."""
        pass

    @cherrypy.expose
    def list(self, univers):
        """Page with all the super hero's from the universe selected."""
        result = '<ol id="univers">'
        if univers == "all":
            for univers in sorted(self.hero):
                result += "<h3>{}</h3>".format(univers)
                for e in sorted(self.hero[univers]):
                    result += '<dt><a href = "fiche?univers={}&name={}">{}</a></dt>'.format(univers, e, e)
            univers = "tous les univers"
        else:
            for e in sorted(self.hero[univers]):
                result += '<dt><a href = "fiche?univers={}&name={}">{}</a></dt>'.format(univers, e, e)
        result += '</ol>'
        return {'liste': result, 'univers': univers}

    @cherrypy.expose
    def fiche(self, univers, name):
        """Page of one super hero."""
        perso = self.hero[univers][name]
        return {'name': name,
                'pouvoir': self.list2html(perso['pouvoir']),
                'famille': self.list2html(perso['famille']),
                'team': self.list2html(perso['team']),
                'ennemis': self.list2html(perso['ennemis']),
                'comments': self.plotcomments(name, univers),
                'univers': univers}

    @cherrypy.expose
    def addcomment(self, univers, name, comment, pseudo):
        """Post route to add a comment to the database."""
        if comment != '' and pseudo != '':
            count = self.count() + 1
            self.comments.append({'pseudo': pseudo, "text": comment, "report": False, "name": name,
                                  'univers': univers, 'id': count})
            self.saveinfo()
        raise cherrypy.HTTPRedirect('/fiche?univers={}&name={}'.format(univers, name))

    def loadinfo(self):
        """Get all the information from the database."""
        try:
            with codecs.open('db.json', 'r', encoding='utf8') as file:
                content = json.loads(file.read(), encoding="utf8")
                return content
        except:
            cherrypy.log('problème base de donnée')
            return {}

    def saveinfo(self):
        """Save all the information to the database."""
        try:
            with codecs.open('db.json', 'w', encoding='utf8') as file:
                file.write(json.dumps(self.info, ensure_ascii=False))
        except:
            cherrypy.log('Saving database failed.')

    def list2html(self, info):
        """Transform a python list into a HTML list."""
        res = '<ol id="list">'
        for e in info:
            res += "<dt>" + e + "</dt>"
        res += '</ol>'
        return res

    def plotcomments(self, name, univers):
        """Set up the HTML code for the comments of a character"""
        toplot = [i for i in self.comments if i['name'] == name]
        res = '<ol id="comments">'
        for i in range(len(toplot)):
            comment = toplot[i]
            res += '''<div id="comment"><dt><b>{}</b>:</dt><dt>{}</dt></div>
            <dt><small>(<a href="reportcomment?univers={}&name={}&i={}"
            onclick="return confirm('Commentaire signalé')">Signaler ce commentaire</a>)
            </small></dt>'''.format(comment['pseudo'], comment['text'], univers, name, i)
        res += '</ol>'
        return res

    @cherrypy.expose
    def reportcomment(self, univers, name, i):
        """Get route to report a comment."""
        comment = [e for e in self.comments if e['name'] == name][int(i)]
        try:
            comment['report'] = True
            self.saveinfo()
        except:
            cherrypy.log(str(comment))
            cherrypy.log('Report failed')
        finally:
            url = '/fiche?univers={}&name={}'.format(univers, name)
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def getcomments(self):
        """Get route to get all the comments."""
        return json.dumps({
            'comments': self.comments
        }, ensure_ascii=False).encode('utf8')

    @cherrypy.expose
    def deletecom(self, idee):
        """Get route to delete a comment."""
        for i in range(len(self.comments)):
            if int(self.comments[i]['id']) == int(idee):
                del self.comments[i]
                self.saveinfo()
                result = 'OK'
                return result.encode('utf8')

    @cherrypy.expose
    def commentok(self, idee):
        """Get route to cancel the report of a comment."""
        for i in range(len(self.comments)):
            if int(self.comments[i]['id']) == int(idee):
                self.comments[i]['report'] = False
                self.saveinfo()
                result = 'OK'
                return result.encode('utf8')


if __name__ == '__main__':
    # Register Jinja2 plugin and tool
    ENV = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    jinja2plugin.Jinja2TemplatePlugin(cherrypy.engine, env=ENV).subscribe()
    cherrypy.tools.template = jinja2tool.Jinja2Tool()
    # Launch web server
    CURDIR = os.path.dirname(os.path.abspath(__file__))
    cherrypy.quickstart(SupaHero(), '', 'server.conf')
