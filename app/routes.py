import csv
import os
import json
import plotly
from app import app
from flask import render_template,flash,url_for,redirect,request,send_file
from app.forms import LoginForm,ProfileForm,AccueilForm
from flask_login import logout_user,current_user,login_user,login_required
from app.models import User
from app.spiders.scraper import facebookScraper
from app.spiders.scraperPage import facebookPage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Image
import plotly.graph_objs as go
import networkx as nx
from werkzeug.utils import secure_filename

scraper = ""
infos=dict()
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/',methods=['GET','POST'])
@app.route('/connexion/',methods=['GET','POST'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('recherche'))
    form = LoginForm()
    if form.validate_on_submit() and request.method=="POST":
        user =User()
        if form.username.data==user.username and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('recherche')
            return redirect(next_page)
        flash('Invalid username or password')
        return redirect(url_for('index'))
    return render_template("login.html",form=form)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/')
@login_required
def profile():
    form =ProfileForm()
    if request.method=="POST":
        if 'file' not in request.files:
            flash('No file part')
            return redirect('profile')
        file=request.files['file']
        if file.filename=='':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    elif request.method=="GET":
        form.username.data=current_user.username
        return render_template("profile.html",form=form)

@app.route('/recherche/')
def recherche():
    form = AccueilForm()
    return render_template("recherche.html",form=form)

@app.route("/recherche/resultats/",methods=['GET','POST'])
def resultat_recherche():
    if request.method=='POST':
        global scraper
        if request.form["pages"]=="Les Personnes":
            scraper = facebookScraper()
            resultats = scraper.recherche(request.form["nom"])
            return render_template("resultats.html", result=resultats,type="personne")
        if request.form["pages"] == "Les Pages":
            scraper=facebookPage()
            resultats = scraper.recherche(request.form["nom"])
            return render_template("resultats.html",result=resultats,type="page")

@app.route('/recherche/resultats/accueil/<nom> <type>')
@login_required
def accueil(nom,type):
    form=AccueilForm()
    global infos
    if type=="personne":
        friends=scraper.recuperer_amis(nom)
        infos=scraper.infos_perso()
        posts=scraper.recuperer_posts(nom)
        scraper.close()
        ids,graphJSON=plot(nom)
        return render_template("accueil.html",form=form,username=nom,friends=friends,posts=posts,ids=ids,graphJSON=graphJSON,type=type,infos=infos)
    else :
        image,publications,nombre_likes=scraper.recuperer_publication(nom)
        nb_abonne, date_creation, nom_précedent=scraper.recuperer_infos_de_page()
        infos['likes']=nb_abonne
        infos['date_creation']=date_creation
        infos["nom"]=nom
        infos['ancienNom']=nom_précedent
        infos['image']=image
        infos['nb_likes']=nombre_likes
        scraper.close()
        return render_template("accueil.html",form=form,username=nom,friends=publications,posts=publications,type=type,infos=infos)

@app.route("/download_csv/<nom> <type>")
def download_csv(nom,type):
    if type=="personne":
        return send_file("/home/sentos/Documents/PycharmProjects/site_FAA/fichiers/friends-{}.csv".format(nom),
                     attachment_filename="friends-{}.csv".format(nom),as_attachment=True)
    else:
        return send_file("/home/sentos/Documents/PycharmProjects/site_FAA/fichiers/post-{}.csv".format(nom),
                     attachment_filename="publications-{}.csv".format(nom),as_attachment=True)

@app.route('/graph/')
def graph():
    return render_template("graphe.html")

def plot(nom):
    datas = []
    with open("fichiers/friends-%s.csv"%nom, 'rt', encoding="utf-8")as f:
        reader = csv.reader(f)
        for row in reader:
            datas.append(row)
    nodes = []
    for i in range(len(datas)):
        nodes.append({"nom": datas[i][0], "url": datas[i][1]})
    links = []
    for i in range(len(datas)):
        links.append({"source": 0, "target": i, "value": 1})

    lists = ['nodes', 'links']
    data = dict()
    data['nodes']=nodes
    data['links']=links
    json.dumps(data)
    print(type(data))

    L = len(data['links'])
    Edges = [(data['links'][k]['source'], data['links'][k]['target']) for k in range(L)]

    G = nx.Graph()
    G.add_edges_from(Edges)

    labels = []
    group = []
    for node in data['nodes']:
        labels.append(node['nom'])
        group.append(node['url'])

    nb = len(nx.nodes(G))

    G1 = nx.random_geometric_graph(nb, 0.125)
    pos = nx.get_node_attributes(G1, 'pos')

    G1.edges.data(Edges)

    dmin = 1
    ncenter = 0
    for n in pos:
        x, y = pos[n]
        d = (x - 0.5) ** 2 + (y - 0.5) ** 2
        if d < dmin:
            ncenter = n
            dmin = d

    for node in G.nodes():
        G.node[node]["pos"] = G1.node[node]['pos']

    p = nx.single_source_shortest_path_length(G1, ncenter)
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        mode='lines')

    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[],
        y=[],
        mode='markers',
        hoverinfo='text',
        text=labels)

    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])


    graphs = [
        dict(
            data=[edge_trace,node_trace],
            layout=dict(
                title='network graph',
                titlefont=dict(size=16),
                showlegend=True,
                scrollZoom= True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[dict(
                    text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002)],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
    ]

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return ids,graphJSON