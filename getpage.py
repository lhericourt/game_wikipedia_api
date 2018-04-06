#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Ne pas se soucier de ces imports
import setpath
from bs4 import BeautifulSoup
from json import loads
from urllib.request import urlopen
from urllib.parse import urlencode, unquote, urldefrag
import unittest

# Si vous écrivez des fonctions en plus, faites-le ici
cache = {}


def validate_link(link):
    """
    Fonction qui vérifie si le lien est interne à wikipedia
    et s'il est valide : utilisation des classes css "new" et "external"
    :param href: lien à tester
    :return: True ou False en fonction de si lien fonctionne ou non
    """
    try:
        # Vérification lien hors de l'espace principal
        if ":" in link["href"]:
            return None

        # On ne tient pas compte des liens qui permettent d'écouter un son
        elif link["href"].startswith("/wiki/API_"):
            return None

        # On ne tient pas compte des liens des images
        elif link["href"].startswith("//upload.wikimedia.org"):
            return None

        # On ne tient pas compte des ancres
        elif link["href"].startswith("#"):
            return None

        # Vérification lien externe ou lien rouge
        elif "external" in link["class"] or "new" in link["class"]:
            return None
    except KeyError:
        pass

    return link["href"][6:]


def getJSON(page):
    params = urlencode({
        'format': 'json',
        'action': 'parse',
        'prop': 'text',
        'redirects': True,
        'page': page})
    API = "https://fr.wikipedia.org/w/api.php"
    response = urlopen(API + "?" + params)
    return response.read().decode('utf-8')


def getRawPage(page):
    parsed = loads(getJSON(page))
    try:
        title = parsed["parse"]["title"]
        content = parsed["parse"]["text"]["*"]
        return title, content
    except KeyError:
        # La page demandée n'existe pas
        return None, None


def getPage(page):
    list_href = []
    global cache

    cache_data = cache.get(page.lower())

    # Traitements si la page n'est pas en cache
    if cache_data is None:
        try:
            title_page, html_page = getRawPage(page)
            soup_page = BeautifulSoup(html_page, "html.parser")

            # Récupération des liens qui sont uniquement dans des paragraphes
            list_p = soup_page.find_all("p")
            count = 0

            for p in list_p:
                list_link = p.find_all("a")

                for link in list_link:

                    # On formate correctement le lien
                    link_OK = validate_link(link)
                    if link_OK is not None:
                        link_OK = urldefrag(unquote(link["href"][6:]))[0]

                    # Si le lien est valide et n'est pas déjà dans la liste des liens on l'ajoute
                    if link_OK is not None and link_OK not in list_href:
                        list_href.append(urldefrag(unquote(link["href"][6:]))[0])
                        count += 1
                        if count > 9:
                            # Ajout des informations de la nouvelle page dans le cache
                            cache[page.lower()] = {"title": title_page,
                                                   "list_href": list_href}
                            return title_page, list_href

            # Ajout des informations de la nouvelle page dans le cache
            cache[page.lower()] = {"title": title_page,
                                   "list_href": list_href}

            return title_page, list_href

        except TypeError:
            return None, []

    # Traitements si la page est dans le cache
    else:
        return cache_data["title"], cache_data["list_href"]


class GetPageTests(unittest.TestCase):
    """
    Classe pour tester les règles de gestion de récupération des liens
    """

    def testGetLinks(self):
        # Vérification que la récupération du titre se fait bien
        self.assertEqual("Utilisateur:A3nm/INF344", getPage("Utilisateur:A3nm/INF344")[0])

        # Vérification que la récupération du titre redirigé
        self.assertEqual("Philosophie", getPage("Philosophique")[0])

        # Vérification que seuls les liens dans des balises <p> sont pris en compte
        self.assertNotIn("Piège", getPage("Utilisateur:A3nm/INF344")[1])

        # Vérification que les liens externes ne sont pas pris en compte
        self.assertNotIn("https://www.telecom-paristech.fr/", getPage("Utilisateur:A3nm/INF344")[1])

        # Vérification que les liens "rouges" ne sont pas pris en compte
        self.assertNotIn("/w/index.php?title=Une_page_qui_n%27existe_pas&amp;action=edit&amp;redlink=1",
                         getPage("Utilisateur:A3nm/INF344")[1])

        # Vérification que les ancres des pages ne sont pas pris en compte
        self.assertNotIn("Philosophie#Frise_chronologique", getPage("Utilisateur:A3nm/INF344")[1])

        # Vérification que les accents sont correctement gérés
        self.assertIn("Réussite", getPage("Utilisateur:A3nm/INF344")[1])

        # Vérification que l'on obtient maximum 10 liens
        self.assertEqual(len(getPage("France")[1]), 10)

        # Vérification que l'on a pas de doublons
        self.assertListEqual(getPage("Utilisateur:A3nm/INF344")[1],
                             ['Pétunia', 'Philosophie', 'Philosophique', 'René_Descartes', 'Geoffrey_Miller',
                              'Réussite'])


if __name__ == '__main__':
    print(getPage("Utilisateur:A3nm/INF344"))

    unittest.main()
