import csv
import time
import sys
import json
import random


from datetime import datetime
from app.modelsScrapers import PersonnesItem,PostItem,AmiItem,MyEncoder

# selenium package
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
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

class facebookScraper(Scraper):

    def __init__(self):
        super().__init__(type="Personnes")
        self.friends=[]
        self.posts=[]

    def recuperer_posts(self,nom):
        self.attendre_elt(2, 10, "a._6-6")

        # sélectionner la liste d'amis
        lien = self.driver.find_element_by_partial_link_text("Journal")
        self.scroller_vers_elt(lien)
        self.click_lien(lien)

        posts = self.parse_posts(3.0)
        self.afficher(posts)
        self.ecrire_dans_fichier_json("fichiers/post-%s" %nom, posts)
        self.posts=posts
        return posts

    def recuperer_amis(self,nom):
        self.afficher("Récupère les amis")
        id=0
        for i in range (0,len(self.items)):
            if self.items[i]['name']==nom:
                id=i
                break
        self.driver.get(self.items[id]['url'])
        self.attendre_elt(2,10,"a._6-6")

        # sélectionner la liste d'amis
        lien = self.driver.find_element_by_partial_link_text("Amis")
        self.scroller_vers_elt(lien)
        self.click_lien(lien)
        #lien[2].send_keys(Keys.ENTER)
        self.attendre_elt(2,10,"div._3cz")

        friends=self.parse_amis(6.5) #7.0
        self.afficher(len(friends))
        self.ecrire_dans_fichier_json("fichiers/ami-%s.json"%nom,friends)

        self.ecrire_dans_fichier_csv(friends,nom)
        self.friends=friends

        return friends

    def infos_perso(self):
        self.afficher("Informations sur l'utilisateur")
        lien = self.driver.find_element_by_partial_link_text("propos")
        self.click_lien(lien)
        self.attendre_elt(2, 10, "div._3cz")
        item = AproposItem()
        lien = self.driver.find_element_by_partial_link_text("Informations générales")
        self.click_lien(lien)
        infos = self.driver.find_elements_by_css_selector("div._4bl7")
        j = 0
        for i in range(1, len(infos)):
            if (infos[i].text.encode("utf-8")).decode('utf-8').replace("'", '"') != '':
                j = i
                break;

        return (infos[j].text.encode("utf-8")).decode('utf-8').replace("'", '"')

    def parse_amis(self,longueur):
            self.scroll_page(longueur)
            items=[]
            amis = self.driver.find_elements_by_css_selector("div._5qo4")
            for ami in amis:
                item=PersonnesItem()
                item["name"] = ami.find_element_by_css_selector("div.fsl > a").text.encode('utf-8')
                item["url"] = ami.find_element_by_tag_name("a").get_attribute("href")
                item["name"]=item["name"].decode('utf-8').replace("'", '"')
                items.append(item)

            self.afficher('fin de la récupération des amis \n')
            return items

    def parse_posts(self,longueur):
        self.scroll_page(longueur)
        items=[]
        liste_posts=self.driver.find_elements_by_css_selector("div.userContentWrapper")
        for post in liste_posts:
            item=PostItem()
            self.pause()
            try:
                item['auteur']=post.find_element_by_css_selector("a.profileLink").text.encode('utf-8')
                item["auteur"] = item["auteur"].decode('utf-8').replace("'", '"')
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['auteur']=""
            try:
                item["date"] = post.find_element_by_css_selector("span.timestampContent").text.encode('utf-8')
                item["date"] = item["date"].decode('utf-8').replace("'", '"')
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['date']=""
            try:
                item["nb_comments"] = post.find_element_by_css_selector("div._36_q > a").text.encode('utf-8')
                item["nb_comments"] = self.split_comment(item["nb_comments"].decode('utf-8').replace("'", '"'))
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['nb_comments']=""
            try:
                item["nb_likes"] = post.find_element_by_css_selector("a._2x4v").text.encode('utf-8')
                item["nb_likes"] = self.split_likes(item["nb_likes"].decode('utf-8').replace("'", '"'))
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['nb_likes']=""
            try:
                item["lien_posts"]=post.find_element_by_css_selector("a._2x4v").get_attribute('href')
                #self.driver.get(item["lien_likes"])
                #self.pause()
            except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                item['lien_posts']=""
            items.append(item)

        self.afficher('fin de la récupération des posts \n')
        return items


    def ecrire_dans_fichier_csv(self,items,nom):
        # ouvrir csv
        with open("fichiers/friends-%s.csv"%nom, 'w') as csvfile:
            fieldnames=["nom","lien vers le compte"]
            writer=csv.DictWriter(csvfile,fieldnames)
            writer.writeheader()
            # boucle
            for ami in items:
                name = ami['name']
                url_profil = ami['url']

                # copier dans le csv
                try:
                    writer.writerow({"nom":name,"lien vers le compte":url_profil})
                except(NoSuchElementException, WebDriverException, StaleElementReferenceException, UnicodeEncodeError):
                    print("Error message - csv")
                finally:
                    pass
        print('fin écriture fichier csv  \n')

    def split_comment(self,comment):
        pos=comment.find("commentaire")
        nb=comment[:pos]
        return nb

    def split_partage(self,partage):
        pos=partage.find("partage")
        nb=partage[:pos]
        return nb

    def split_likes(self,comment):
        pos=comment.find("\n")
        nb=comment[:pos]
        return nb

    def muliplication(self,chaine):
        if chaine.endswith("M"):
            chaine = chaine.replace("M", "")
            return int(chaine) * 1000000
        if chaine.endswith("K"):
            chaine = chaine.replace("K", "")
            return int(chaine) * 1000

    def split_nb_likes(self, chaine):
            pos = chaine.find("personnes")
            pos1 = chaine.find("ça")
            a = chaine[:pos]
            b = chaine[pos1 + 2:]
            return b, a