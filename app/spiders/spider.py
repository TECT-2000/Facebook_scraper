import csv
import time
import sys
import json
import random
from app.modelsScrapers import PersonnesItem,PagesItem,MyEncoder
from app import app
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


class Scraper():
    allowed_domains=["facebook.com"]
    start_urls=["https://www.facebook.com/"]


    def __init__(self,type):
        options=webdriver.ChromeOptions()
        options.add_argument("headless")
        self.driver = webdriver.Chrome(chrome_options=options)
        self.items = []
        self.type=type
        self.nb_likes = 0

    def login(self):
        url = "http://www.facebook.com"
        email=app.config['EMAIL']
        mdp=app.config['MDP']
        self.driver.get(url)
        self.attendre_elt(1,10,"login_form")
        self.pause()
        self.afficher("Connecté à Facebook - 1")

        self.remplir_formulaire(email,mdp)

        self.attendre_elt(4,10,'q')
        self.pause()
        self.afficher("Profil connecté à Facebook - 1")

    def recherche(self,nom):
        self.login()
        """ recherche dans la page d'accueil de facebook """
        search_item=nom
        self.recherche_personne(search_item)

        """ se rassurer que la recherche est finie"""
        self.pause()
        self.afficher("Fin de la recherche avec mot clé : " + search_item)

        type = self.type
        self.attendre_elt(3,10,type)
        lien = self.recherche_elt(4,type)
        self.click_lien(lien)

        if self.type=="Personnes":
            items=self.parse_Personnes(1.0) #3.0
        else:
            items = self.parse_Pages(1.0)

        #self.ecrire_dans_fichier_json("fichiers/{}_recherche.json".format(self.type),items)
        self.items=items
        return items

    def parse_Pages(self,longueur):
            self.scroll_page(longueur)
            items=[]
            profils = self.driver.find_elements_by_css_selector("div._5bl2")
            for profil in profils:
                item=PagesItem()
                item["image"] = profil.find_element_by_css_selector("img._1glk").get_attribute("src")
                item["name"] = profil.find_element_by_css_selector("a._32mo").text.encode('utf-8')
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});",
                    profil.find_element_by_css_selector("a._32mo"))
                item["url"] = profil.find_element_by_css_selector("a._32mo").get_attribute('href')
                item["nb_likes"] = profil.find_element_by_css_selector("div._pac").text.encode('utf-8')
                item["name"]=item["name"].decode('utf-8').replace("'",'"')
                item["nb_likes"]=item["nb_likes"].decode('utf-8').replace("'", '"')
                a,b=self.split_nb_likes(item["nb_likes"])
                item['job']=a
                item["nb_likes"]=b
                items.append(item)


            self.afficher('fin de la récupération des résultats \n')
            return items

    def parse_Personnes(self,longueur):
            self.scroll_page(longueur)
            items=[]
            profils = self.driver.find_elements_by_css_selector("div._4p2o")
            for profil in profils:
                item=PersonnesItem()
                item["image"] = profil.find_element_by_css_selector("img._1glk").get_attribute("src")
                item["name"] = profil.find_element_by_css_selector("a._32mo").text.encode('utf-8')
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});",
                    profil.find_element_by_css_selector("a._32mo"))
                item["url"] = profil.find_element_by_css_selector("a._32mo").get_attribute('href')
                item["job"] = profil.find_element_by_css_selector("div._pac").text.encode('utf-8')
                item["name"]=item["name"].decode('utf-8').replace("'",'"')
                item["job"]=item["job"].decode('utf-8').replace("'", '"')
                items.append(item)


            self.afficher('fin de la récupération des résultats de recherche \n')
            return items

    def ecrire_dans_fichier_json(self,nomFichier,donnees):
        with open(nomFichier,"w") as f:
            file=json.dumps(donnees,sort_keys=True,cls=MyEncoder)
            json.dump(file,f)

    def afficher(self,message):
        print(message)

    def click_lien(self,lien):
        lien.send_keys(Keys.ENTER)
        self.pause()

    def recherche_personne(self,item):
        find = self.driver.find_element_by_name("q")
        find.clear()
        find.send_keys(item)
        find.send_keys(Keys.RETURN)

    def remplir_formulaire(self,email,mdp):
        elem = self.recherche_elt(5,"email")
        elem.clear()
        elem.send_keys(email)
        password = self.recherche_elt(1,"pass")
        password.clear()
        password.send_keys(mdp)
        elem.send_keys(Keys.RETURN)

    def recherche_elt(self,numero,selector):
        try:
            if numero==1:
                return self.driver.find_element_by_id(selector)
            elif numero==2:
                return self.driver.find_element_by_css_selector(selector)
            elif numero==3:
                return self.driver.find_element_by_tag_name(selector)
            elif numero==4:
                return self.driver.find_element_by_link_text(selector)
            elif numero==5:
                return self.driver.find_element_by_name(selector)
        except (NoSuchElementException, WebDriverException, StaleElementReferenceException):
                return ""

    def attendre_elt(self,categorie,temps,input):
        if categorie==1:
            try:
                WebDriverWait(self.driver, temps).until(EC.presence_of_element_located(
                    (By.ID, input))
                )
            except (TimeoutException):
                sys.exit("Error message - temps écoulé")
        elif categorie == 2:
                try:
                    WebDriverWait(self.driver, temps).until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, input))
                    )
                except (TimeoutException):
                    sys.exit("Error message - temps écoulé")
        elif categorie == 3:
                try:
                    WebDriverWait(self.driver, temps).until(EC.element_to_be_clickable(
                        (By.LINK_TEXT, input))
                    )
                except (TimeoutException):
                    sys.exit("Error message - temps écoulé")
        elif categorie == 4:
                try:
                    WebDriverWait(self.driver, temps).until(EC.element_to_be_clickable(
                        (By.NAME, input))
                    )
                except (TimeoutException):
                    sys.exit("Error message - temps écoulé")

    def scroller_vers_elt(self,elt):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});", elt)

    def scroll_page(self,longueur):
        # scroll down
        print("je scrolle %s"%longueur)
        scheight = .1
        while scheight < longueur:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight*%s);" % scheight)
            scheight += .2
            self.pause()
        print("Fin du scroll")

    def close(self):
        self.driver.close()
        self.afficher("fermeture du driver")

    # fonction pause
    def pause(self):
        time_break = random.randint(5, 10)
        return time.sleep(time_break)

    def split_nb_likes(self,chaine):
        pos = chaine.find("personnes")
        pos1=chaine.find("ça")
        a = chaine[:pos]
        b=chaine[pos1+2:]
        return b,a