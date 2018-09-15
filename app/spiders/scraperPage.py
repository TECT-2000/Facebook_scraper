import csv
import time
import sys
import json
import scrapy
import random
from datetime import datetime
from app.modelsScrapers import MyEncoder,PublicationItem,PagesItem

# selenium package
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from app.spiders.spider import Scraper

class facebookPage(Scraper):

    def __init__(self):
        super().__init__("Pages")
        self.publications = []

    def recuperer_publication(self, nom):
        self.afficher("Récupère les publications")
        id = 0
        for i in range(0, len(self.items)):
            if self.items[i]['name'] == nom:
                id = i
                break
        image=self.items[id]['image']
        nb_likes=self.items[id]['nb_likes']
        print(self.items[id]['nb_likes'])
        self.driver.get(self.items[id]['url'])
        self.attendre_elt(2, 10, "div._r_m")
        lien = self.recherche_elt(4, "Publications")
        posts = self.parse_publications(3.0)
        self.afficher(posts)
        self.ecrire_dans_fichier_json("fichiers/post-%s" % self.items[id]['name'], posts)
        self.afficher(len(posts))

        self.ecrire_dans_fichier_csv(posts, nom)
        self.publications = posts

        return image,posts,nb_likes

    def recuperer_infos_de_page(self):
        lien = self.recherche_elt(4, "Communauté")
        self.click_lien(lien)
        nb_jaime=0
        infos=self.driver.find_elements_by_css_selector("div._3xom")
        if infos:
            nb_jaime=infos[1].text.encode('utf-8')
            nb_jaime=self.muliplication(nb_jaime.decode('utf-8').replace("'", '"'))
        #total_abonne=infos[2].text.encode('utf-8')
        #total_abonne=total_abonne.decode('utf-8').replace("'", '"')

        lien = self.recherche_elt(4, "Infos et publicités")
        self.click_lien(lien)
        date_creation=self.recherche_elt(2,"span._2ien").text.encode('utf-8')
        if date_creation !='':
            date_creation=date_creation.decode('utf-8').replace("'", '"')
        nom_precedent=self.recherche_elt(2,"span._50f7")
        if nom_precedent !="":
            nom_precedent=nom_precedent.text.encode('utf-8')
            nom_precedent=nom_precedent.decode('utf-8').replace("'", '"')

        #print(nb_jaime,nom_precedent,date_creation)

        return  nb_jaime,date_creation,nom_precedent

    def parse_publications(self,longueur):
        self.scroll_page(longueur)
        items=[]
        liste_posts=self.driver.find_elements_by_css_selector("div.userContentWrapper")
        for post in liste_posts:
            item=PublicationItem()
            try:
                item['auteur']=post.find_element_by_css_selector("span.fwb > a").text.encode('utf-8')
                item["auteur"] = item["auteur"].decode('utf-8').replace("'", '"')
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['auteur']=""
            try:
                item["date"] = post.find_element_by_css_selector("span.timestampContent").text.encode('utf-8')
                item["date"] = item["date"].decode('utf-8').replace("'", '"')
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['date']=""
            try:
                item["nb_comments"] = post.find_element_by_css_selector("a._-56").text.encode('utf-8')
                item["nb_comments"] = self.split_comment(item["nb_comments"].decode('utf-8').replace("'", '"'))
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['nb_comments']=""
            try:
                item["nb_partages"] = post.find_element_by_css_selector("a._2x0m").text.encode('utf-8')
                item["nb_partages"] = self.split_partage(item["nb_partages"].decode('utf-8').replace("'", '"'))
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['nb_partages']=""
            try:
                item["nb_likes"] = post.find_element_by_css_selector("a._2x4v").text.encode('utf-8')
                item["nb_likes"] = self.split_likes(item["nb_likes"].decode('utf-8').replace("'", '"'))
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['nb_likes']=""
            try:
                item["lien_posts"]=post.find_element_by_css_selector("a._-56").get_attribute('href')
                #self.pause()
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['lien_posts']=""
            try:
                item["texte"]=post.find_element_by_css_selector("p").text.encode('utf-8')
                item["texte"]=item["texte"].decode('utf-8').replace("'", '"')
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['texte']=""
            items.append(item)

        self.afficher('fin de la récupération des résultats \n')
        return items

    def ecrire_dans_fichier_csv(self, items, nom):
        # ouvrir csv
        with open("fichiers/publications-%s.csv" % nom, 'w') as csvfile:
            fieldnames = ["Auteur", "nb_comments","nb_likes","texte","date","nb_partages","taux d'engagement"]
            writer = csv.DictWriter(csvfile, fieldnames)
            writer.writeheader()
            # boucle
            for publication in items:
                name = publication['auteur']
                date = publication['date']
                nb_comments=publication['nb_comments']
                nb_likes=publication['nb_likes']
                nb_partages=publication['nb_partages']
                texte=publication['texte']
                # copier dans le csv
                try:
                    writer.writerow({"Auteur": name, "date": date,"nb_comments":nb_comments,"nb_likes":nb_likes,"nb_partages":nb_partages,"texte":texte})
                except(NoSuchElementException, WebDriverException, StaleElementReferenceException, UnicodeEncodeError):
                    print("Error message - csv")
                finally:
                    pass
        print('fin fichier csv  publications\n')

    def split_comment(self,comment):
        pos=comment.find("commentaire")
        nb=comment[:pos]
        return nb

    def split_partage(self,partage):
        pos=partage.find("partage")
        nb=partage[:pos]
        return nb

    def muliplication(self,chaine):
        if chaine.endswith("M"):
            chaine = chaine.replace("M", "")
            return int(chaine) * 1000000
        if chaine.endswith("K"):
            chaine = chaine.replace("K", "")
            return int(chaine) * 1000


    def split_likes(self,chaine):
        if  "K" in chaine:
            """pos = chaine.find("K")
            str = chaine[:pos]
            chaine=self.enleve_virgule(str)"""
            return chaine
        if "M" in chaine:
            """pos = chaine.find("M")
            str=chaine[:pos]
            self.enleve_virgule(str)"""
            return chaine
        elif "\n" in chaine:
            pos = chaine.find("\n")
            return float(chaine[:pos])
        else:
            pos = chaine.find(" ")
            return float(chaine[:pos])

    def split_nb_likes(self, chaine):
            pos = chaine.find("personnes")
            pos1 = chaine.find("ça")
            a = chaine[:pos]
            b = chaine[pos1 + 2:]
            return b, a

    def enleve_virgule(self,chaine):
        if "," in chaine:
            chaine=chaine.replace(',', ".")
            return chaine