#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Ne pas se soucier de ces imports
import setpath
from flask import Flask, render_template, session, request, redirect, flash
from getpage import getPage

app = Flask(__name__)

app.secret_key = "TODO: mettre une valeur secrète ici"


@app.route('/', methods=['GET'])
def index():
    session["score"] = 0
    return render_template('index.html')

# Si vous définissez de nouvelles routes, faites-le ici

@app.route('/new-game', methods=['POST'])
def new_game():
    session["article"] = request.form["title"]
    return redirect('/game')


@app.route('/game', methods=['GET'])
def game():
    title_page, list_href = getPage(session["article"])

    # Stockage du résultat dans la session, pour être en mesure de vérifier
    # que le lien sélectionné par l'utilisateur proviendra bien de cette liste
    session["list_href"] = list_href

    # Cas ou la page demandée n'existe pas
    if title_page is None:
        flash("/!\\ La page wikipédia demandée n'existe pas /!\\", "error")
        return redirect('/')

    # Cas ou aucun lien n'a été remonté
    elif not list_href:
        flash("/!\\ La page wikipédia demandée ne possède aucun lien /!\\", "error")
        return redirect('/')

    # Cas le joueur a trouvé la page philosophie
    elif title_page.lower() == "philosophie":
        flash("/!\\ Bravo vous avez gagné la partie en {} coup(s) /!\\".format(session["score"]), "success")
        session["score"] = 0
        #return render_template('index.html')
        return redirect('/')

    else:
        return render_template('game.html', title=title_page, href=list_href, score=session["score"])


@app.route('/move', methods=['POST'])
def move():

    # Vérification de la cohérence du score (cas multi-onglets)
    if not session["score"] == int(request.form["score"]):
        flash("/!\\ Cette page n'est pas la dernière depuis laquelle vous avez joué, "
              "la partie reprend avec les dernières informations reçues /!\\", "error")
        return redirect('/game')

    elif request.form["list_links"] not in session["list_href"]:
        flash("/!\\ Vous avez triché en modifiant directement le code HTML,"
              " veuillez sélectionner un des liens ci-dessous /!\\", "error")
        return redirect('/game')

    # Mise à jour du score dans une variable de session
    try:
        session["score"] += 1
    except KeyError:
        session["score"] = 1

    # Mise à jour de la variable de session article
    session["article"] = request.form["list_links"]
    return redirect('/game')

if __name__ == '__main__':
    app.run(debug=True)

