# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import pytz
from psycopg2 import IntegrityError

from datetime import datetime
from odoo.exceptions import ValidationError
from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request, Response
from werkzeug.exceptions import NotFound
import logging
import base64
from odoo.addons.website_form.controllers.main import WebsiteForm


class Api_recrutement(http.Controller):

    @http.route("/api_recrutement",auth="public", type="http", methods=["GET","POST"], website=False,csrf=False)
    def index(self, **kwargs):

        jobs= request.env["hr.job"].sudo().search([],limit=8,order="date_cloture desc")
        logging.info(kwargs)
        json_jobs=[]
        for job in jobs:
            json_jobs.append({"values":{"titre":job.name,"detail":job.web_description,"closedate":str(job.date_cloture),"contexte":job.context,"qualification":job.qualification,"online_id":job.id}})

        res = json.dumps(json_jobs)
        return res

    @http.route("/api_recrutement/education", auth="public", type="http", methods=["GET", "POST"], website=False, csrf=False)
    def get_education(self, **kwargs):

        req = kwargs["id"]
        id = int(json.loads(req))
        educations = request.env["hr.applicant.education"].sudo().search([("candidat_id","=",id)], limit=10)
        logging.info(kwargs)
        json_educ = []
        for education in educations:
            json_educ.append({"values": {"institution": education.institution, "name": education.name,
                                         "qualification": education.qualification,"date_debut":str(education.date_debut),"date_fin":str(education.date_fin) ,"candidat_id":int(education.candidat_id.id),"online_id": int(education.id)}})

        res = json.dumps(json_educ)
        return res

    @http.route("/api_recrutement/formation", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def get_formation(self, **kwargs):

        req = kwargs["id"]
        id = int(json.loads(req))
        formations = request.env["hr.applicant.formation"].sudo().search([("candidat_id", "=", id)], limit=10)
        logging.info(kwargs)
        json_format = []
        for formation in formations:
            json_format.append({"values": {"institution": formation.institution, "name": formation.name,
                                         "qualification": formation.qualification,
                                         "date_debut": str(formation.date_debut), "date_fin": str(formation.date_fin),
                                         "candidat_id": int(formation.candidat_id.id), "online_id": int(formation.id)}})

        res = json.dumps(json_format)
        return res

    @http.route("/api_recrutement/experience", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def get_experience(self, **kwargs):

        req = kwargs["id"]
        id = int(json.loads(req))
        experiences = request.env["hr.applicant.experience"].sudo().search([("candidat_id", "=", id)], limit=10)
        logging.info(kwargs)
        json_expr = []
        for experience in experiences:
            json_expr.append({"values": {"name": experience.name, "entreprise": experience.entreprise_id.name,
                                         "taches":experience.taches,
                                         "date_debut": str(experience.date_debut), "date_fin": str(experience.date_fin),
                                         "candidat_id": int(experience.candidat_id.id), "online_id": int(experience.id)}})

        res = json.dumps(json_expr)
        return res

    @http.route("/api_recrutement/langue", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def get_langue(self, **kwargs):


        langues = request.env["hr.applicant_language"].sudo().search([])
        logging.info(kwargs)
        json_lang = []
        for langue in langues:
            json_lang.append({"values": {"name": langue.name, "level": 0.0,
                                         "candidat_id":0, "online_id": int(langue.id)}})

        res = json.dumps(json_lang)
        return res

    @http.route("/api_recrutement/competence", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def get_competence(self, **kwargs):
        req = kwargs["id"]
        id = int(json.loads(req))
        competences = request.env["hr.applicant_competence_relation"].sudo().search([("candidat_id", "=", id)])
        logging.info(kwargs)
        json_lang = []
        for competence in competences:
            json_lang.append({"values": {"name": competence.competence_id.name, "level": float(80.0),
                                         "candidat_id": id, "online_id": int(competence.id)}})

        res = json.dumps(json_lang)
        return res

    @http.route("/api_recrutement/lcomp", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def get_lcomp(self, **kwargs):

        competences = request.env["hr.applicant_domaine"].sudo().search([])
        logging.info(kwargs)
        json_lang = []
        for competence in competences:
            json_lang.append({"values": {"name": competence.name,
                                         "online_id": int(competence.id)}})

        res = json.dumps(json_lang)
        return res

    @http.route("/api_recrutement/languecandidat", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def get_languecandidat(self, **kwargs):

        id = kwargs["id"]
        logging.info(f"========================= l'id ' : {id} et type : {type(id)}")
        langues = request.env["hr.applicant_language_relation"].sudo().search([("candidat_id","=",int(id))])
        logging.info(f"========================= les langues candidat : {langues}")
        json_lang = []
        for langue in langues:
            logging.info(f"========================= la langue candidat : {langue}")
            json_lang.append({"candidat_id": id, "level": langue.level,"online_id": int(langue.language_id.id)})

        res = json.dumps(json_lang)
        return res

    @http.route("/api_recrutement/candidat", auth="public", type="http", methods=["GET", "POST"], website=False,csrf=False)
    def get_candidat(self, **kwargs):
        candidats = request.env["hr.applicant.candidate"].sudo().search([("id","=",int(kwargs["id"]))], limit=1)
        logging.info(f"========= l'id du candidat {kwargs}")

        for candidat in candidats:
            json_candidat={"values": {"nom": candidat.name, "postnom": candidat.postnom,
                                         "prenom": candidat.prenom,"email":candidat.email,"password":candidat.password,
                                         "age": int(candidat.age), "annee_naissance":candidat.annee_naissance,
                                         "adresse": candidat.adresse,"ville":candidat.ville,"online_id": int(candidat.id)}}
        res = json.dumps(json_candidat)
        logging.info(f"========= le resultat envoyé dans get_all est : {res}")
        return res

    @http.route("/api_recrutement/createcandidat", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def create_candidat(self, **kwargs):

        req=kwargs["candidate"]
        jvalue=json.loads(req)
        jvalue["annee_naissance"] =int(jvalue["annee_naissance"])
        jvalue["name"]=jvalue.pop("nom")
        logging.info(f"========== jvalues {jvalue}")

        candidat = request.env["hr.applicant.candidate"].sudo().create(jvalue)

        json_candidat={"values": {"nom": candidat.name, "postnom": candidat.postnom,
                    "prenom": candidat.prenom,"email":candidat.email,"password":candidat.password,
                    "age": int(candidat.age), "annee_naissance": candidat.annee_naissance,
                    "adresse": candidat.adresse, "ville": candidat.ville, "online_id": int(candidat.id)}}

        logging.info(f"========== kwargs {kwargs}")
        logging.info(f"========== params {request.params}")
        res = json.dumps(json_candidat)
        return res

    @http.route("/api_recrutement/createlanques", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def create_langues(self, **kwargs):

        req = kwargs["langues"]
        id = int(kwargs["candidat_id"])
        logging.info(f"============================================= candidat id:{id} id type{type(id)}")

        lagrel=request.env["hr.applicant_language_relation"].sudo().search([("candidat_id","=",id)])
        lgs=[]
        logging.info(f"============================================= langues du candidat:{lagrel}")
        for lg in lagrel:
            lgs.append(lg.language_id.id)

        strreq=str(req)
        logging.info(f"============================================= langues envoyées:{strreq} et de type {type(strreq)}")

        logging.info(f"============================================= id des langues du candidat:{lgs}")

        jlangues=json.loads(strreq)
        logging.info("============================================= requette  et type:")
        logging.info(type(jlangues))
        logging.info(jlangues)

        res=False
        for lang in jlangues:
            langue=dict(lang)
            logging.info(f"============================================= langue : {langue} et type {type(langue)}")
            logging.info(langue)
            if "online_id" in langue:
                if (langue["online_id"] not in lgs):
                    lg = request.env["hr.applicant_language_relation"].sudo().create({"language_id":int(langue["online_id"]),"candidat_id":int(langue["candidat_id"]),"level":int(langue["level"])})
                else:
                    lg=request.env["hr.applicant_language_relation"].sudo().search([("candidat_id","=",id),("language_id","=",int(langue["online_id"]))],limit=1).write({"level":int(langue["level"])})
            res=True
        return Response(json.dumps(res), content_type='application/json')

    @http.route("/api_recrutement/createexperience", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def create_experience(self, **kwargs):

        req=kwargs["experience"]
        jvalue=json.loads(req)
        id_entreprise=False
        nom_entreprise=jvalue["entreprise"]
        if jvalue["entreprise"]:
            entreprise = request.env["hr.applicant.experience.entreprise"].sudo().search([("name","=",str(nom_entreprise))], limit=1)
            logging.info(f"========== Entreprise avant if {entreprise}")
            if entreprise:
                id_entreprise=entreprise.id
                nom_entreprise=entreprise.name
            else:
                entreprise = request.env["hr.applicant.experience.entreprise"].sudo().create({"name":nom_entreprise})
                id_entreprise = entreprise.id

        jvalue["entreprise"]=id_entreprise
        logging.info(f"========== jvalues {jvalue}")
        logging.info(f"========== Entreprise {nom_entreprise}")

        experience = request.env["hr.applicant.experience"].sudo().create(jvalue)

        json_experience={"values": {"name": experience.name, "entreprise": nom_entreprise,
                    "date_debut": str(experience.date_debut),"date_fin":str(experience.date_fin),"taches":experience.taches,
                    "candidat_id": int(experience.candidat_id.id),"online_id":int(experience.id)}}

        logging.info(f"========== kwargs {kwargs}")
        logging.info(f"========== params {request.params}")
        res = json.dumps(json_experience)
        return res

    @http.route("/api_recrutement/createeducation", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def create_education(self, **kwargs):

        req = kwargs["education"]
        jvalue = json.loads(req)

        education = request.env["hr.applicant.education"].sudo().create(jvalue)

        json_education = {"values": {"name": education.name, "institution": education.institution,
                                      "date_debut": str(education.date_debut), "date_fin": str(education.date_fin),
                                      "qualification": education.qualification,
                                      "candidat_id": int(education.candidat_id.id), "online_id": int(education.id)}}

        logging.info(f"========== kwargs {kwargs}")
        logging.info(f"========== params {request.params}")
        res = json.dumps(json_education)
        return res

    @http.route("/api_recrutement/createformation", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def create_formation(self, **kwargs):

        req = kwargs["formation"]
        jvalue = json.loads(req)

        formation = request.env["hr.applicant.formation"].sudo().create(jvalue)

        json_formation = {"values": {"name": formation.name, "institution": formation.institution,
                                      "date_debut": str(formation.date_debut), "date_fin": str(formation.date_fin),
                                      "qualification": formation.qualification,
                                      "candidat_id": int(formation.candidat_id.id), "online_id": int(formation.id)}}

        logging.info(f"========== kwargs {kwargs}")
        logging.info(f"========== params {request.params}")
        res = json.dumps(json_formation)
        return res

    @http.route("/api_recrutement/createcandidature", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def create_candidature(self, **kwargs):

        req = kwargs["candidature"]
        jvalue = json.loads(req)

        candidature = request.env["hr.applicant"].sudo().create(jvalue)

        json_candidature = {"values": {"name": candidature.name, "job_id": candidature.job_id.id,
                                      "candidat_id": str(candidature.candidat_id.id),"online_id": int(candidature.id)}}

        logging.info(f"========== kwargs {kwargs}")
        logging.info(f"========== params {request.params}")
        res = json.dumps(json_candidature)
        return res

    @http.route("/api_recrutement/createcompetence", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def get_listcompetence(self, **kwargs):

        req = kwargs["competences"]
        logging.info(f"============================== kwargs: {kwargs}")
        jvalue = json.loads(req)
        candidat=0
        for competence in jvalue:
            if "competence_id" in competence:
                if request.env["hr.applicant_competence_relation"].sudo().search([("competence_id","=",competence["competence_id"]),("candidat_id","=",competence["candidat_id"])]):
                    candidat =competence["candidat_id"]
                else:

                    request.env["hr.applicant_competence_relation"].sudo().create(competence)
                    candidat = competence["candidat_id"]

        competences = request.env["hr.applicant_competence_relation"].sudo().search([("candidat_id","=",competence["candidat_id"])])

        json_lang = []
        for competence in competences:
            compt=request.env["hr.applicant_domaine"].sudo().search([("id","=",competence.competence_id)],limit=1)
            name = compt.name
            json_lang.append({"values": {"name": name,
                                         "online_id": int(competence.id)}})
        res = json.dumps(json_lang)
        return res
    @http.route("/api_recrutement/connexion", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def check_connexionn(self, **kwargs):

        candidat = request.env["hr.applicant.candidate"].sudo().search([("email", "=", str(kwargs["email"])),("password", "=", str(kwargs["password"]))], limit=1)
        json_return = {"online_id": 0, "state": False}
        if candidat:

            logging.info(f"========== la candidat dans connexion {candidat.email} et {candidat.password} son id: {candidat.id}")
            json_return = {"online_id": int(candidat.id), "state": True}

        logging.info(f"========== kwargs dans connexion {kwargs}")

        res = json.dumps(json_return)
        return res

    @http.route("/api_recrutement/model/delete", auth="public", type="http", methods=["GET", "POST"], website=False,csrf=False)
    def delete(self, **kwargs):
        model_name= kwargs["model"]
        domain = kwargs["domain"]
        candidat_id = kwargs["candidat_id"]
        logging.info(f"*************************************** Delete model :{model_name} domain : {domain} candidat_id :{candidat_id}")
        if model_name and domain:
            name, value = domain.split("=")
            logging.info(f"*************************************** Delete name :{name} value : {value[1:][:-1]}")
            if name:
                competence=request.env["hr.applicant_domaine"].sudo().search([("name","=",value[1:][:-1])],limit=1).id
                in_domain=[("competence_id","=",competence),("candidat_id","=",int(candidat_id))]
                models = request.env[model_name].sudo().search(in_domain)
                logging.info(f"**************************************** records {models} le domain est : {in_domain}")
                for model in models:
                    model.unlink()
                if models:
                    return json.dumps(True)

        return json.dumps(False)
    @http.route("/membres", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def show_membres(self, **kwargs):

        return Response(json.dumps({"Plantes": [{"name": 'monstera',"category": 'classique',"prix":15,"id": '1ed',"isBestSale": True,"light": 2,"water": 3,"cover": "monstera"}]}), content_type='application/json')

    @http.route("/reactApp", auth="public", type="http", methods=["GET", "POST"], website=False,
                csrf=False)
    def show_react(self, **kwargs):


        return """
        <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
        <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
        <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
     
    <head>
      <title>Title</title>
      <!-- Required meta tags -->
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    
      <!-- Bootstrap CSS v5.2.1 -->
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-iYQeCzEYFbKjA/T2uDLTpkwGzCiq6soy8tYaI1GyVh/UjpbCx/TYkiZhlZB6+fzT" crossorigin="anonymous">
    
    </head>

    <body>
      <header>
    
        <nav class="navbar navbar-expand-sm navbar-dark text-muted " style="background-color: #e3f2fd;">
            <a class="navbar-brand" href="#">Navbar</a>
            <button class="navbar-toggler d-lg-none" type="button" data-bs-toggle="collapse" data-bs-target="#collapsibleNavId" aria-controls="collapsibleNavId"
                aria-expanded="false" aria-label="Toggle navigation"></button>
            <div class="collapse navbar-collapse" id="collapsibleNavId">
                <ul class="navbar-nav me-auto mt-2 mt-lg-0">
                    <li class="nav-item">
                        <a class="nav-link active" href="#" aria-current="page">Home <span class="visually-hidden">(current)</span></a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Link</a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="dropdownId" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Dropdown</a>
                        <div class="dropdown-menu" aria-labelledby="dropdownId">
                            <a class="dropdown-item" href="#">Action 1</a>
                            <a class="dropdown-item" href="#">Action 2</a>
                        </div>
                    </li>
                </ul>
                <form class="d-flex my-2 my-lg-0">
                    <input class="form-control me-sm-2" type="text" placeholder="Search">
                    <button class="btn btn-outline-success my-2 my-sm-0" type="submit">Search</button>
                </form>
            </div>
        </nav>
    
      </header>
      <main>
        
        
        <div id="root"></div>
        
        <section text-center>
         
        </section>
 
      </main>
      <footer class>
       
        <script>
          var triggerEl = document.querySelector('#navId a')
          bootstrap.Tab.getInstance(triggerEl).show() // Select tab by name
        </script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"
          integrity="sha384-oBqDVmMz9ATKxIep9tiCxS/Z9fNfEXiDAYTujMAeBAsjFuCZSmKbSSUnQlmh/jp3" crossorigin="anonymous">
        </script>
    
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.1/dist/js/bootstrap.min.js"
          integrity="sha384-7VPbUDkoPSGFnVtYi0QogXtr74QeVeeIs99Qfg5YCF+TidwNdjvaKZX19NZ/e6oz" crossorigin="anonymous">
        </script>
      </footer>
    </body>
        
        
        <script type="text/babel">
            function Card_Group(){
            
            return(
            <div class="container p-3">
                <div class="card-group">
                  <div class="card">
                    <div class="card-header">
                      Header
                    </div>
                    <div class="card-body" id="root">
                      <h4 class="card-title">Title</h4>
                      <p class="card-text">Text</p>
                    </div>
                    <div class="card-footer text-muted">
                      Footer
                    </div>
                  </div>
                  <div class="card">
                    <img class="card-img-top" src="holder.js/100x180/" alt="Card image cap"/>
                    <div class="card-body">
                      <h4 class="card-title">Title</h4>
                      <p class="card-text">Text</p>
                    </div>
                  </div>
                </div>
              </div>
            )
            }
            function Banner() {
                const title = "La maison jungle"
                  return (
                  <h1>{title.toUpperCase()}</h1>
                  )
                }
                
                function Cart() {
                const monsteraPrice = 8
                const ivyPrice = 10
                const flowerPrice = 15
                return (<div>
                    <h2>Panier</h2>
                    <ul>
                    <li>Monstera : {monsteraPrice}€</li>
                     <li>Lierre : {ivyPrice}€</li>
                     <li>Fleurs : {flowerPrice}€</li>
                    </ul>
                      Total : {monsteraPrice + ivyPrice + flowerPrice }€
                      </div>)
                }
            
            ReactDOM.render(<Card_Group/>, document.getElementById('root'))

            
        </script>
        """
