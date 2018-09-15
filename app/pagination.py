from datetime import datetime
from threading import Timer


def muliplication(chaine):
    if chaine.endswith("M"):
        chaine = chaine.replace("M", "")
        return int(chaine) * 1000000
    if chaine.endswith("K"):
        chaine = chaine.replace("K", "")
        return int(chaine) * 1000

    return chaine

nb="980 M"
print(type(nb))
print(muliplication(nb))