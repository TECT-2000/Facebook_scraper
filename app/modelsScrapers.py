from scrapy.item import Item,Field
from json import JSONEncoder

class MyEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

class PersonnesItem(Item):
    name = Field()
    url = Field()
    image = Field()
    job = Field()
    
class AproposItem(Item):
    date_naissance=Field()
    telephone=Field()
    adresse=Field()
    sexe=Field()
    quartier=Field()

class AmiItem(Item):
    nom = Field()
    url = Field()

class PostItem(Item):
    auteur=Field()
    lien_posts=Field()
    nb_likes=Field()
    date=Field()
    nb_comments=Field()


class PagesItem(PersonnesItem):
    nb_likes=Field()

class PublicationItem(PostItem):
    nb_partages=Field()
    texte=Field()
