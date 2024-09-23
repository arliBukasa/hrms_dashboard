# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from datetime import date, datetime, timedelta
from odoo import tools, _
from odoo.modules.module import get_module_resource


class Job(models.Model):
    _inherit = "hr.job"

    lieu_travail = fields.Char(string="Lieu de Travail")
    date_cloture = fields.Date(string="Date de Cloture")
    sector = fields.Many2one("hr.applicant_sector", string="Secteur")
    qualification = fields.Html(string="Qualification")
    departement = fields.Char(string="Departement|Service")
    web_description = fields.Html(string="Détail du poste")
    website_description = fields.Html('Website description', default="")
    num_ref = fields.Char(string="Numero référence")
    experience = fields.Char('Expérience| Work type')
    dossier = fields.Html(string="Dossier")
    context = fields.Html(string="Context")
    publication_state = fields.Selection([("red", "Red"), ("green", "Green"), ("yellow", "Yellow")],
                                         string='Publication status', default="green", compute="_compute_published")
    date_cloture = fields.Date(default=fields.Date.today())

    @api.depends('date_cloture')
    def _compute_published(self):
        for job in self:
            if job.date_cloture:
                if job.date_cloture - timedelta(days=2) > (datetime.today()).date():
                    job.publication_state = "green"
                elif job.date_cloture >= (datetime.today()).date():
                    job.publication_state = "yellow"
                if job.date_cloture < (datetime.today()).date():
                    job.publication_state = "red"
            else:
                job.date_cloture = (datetime.today()).date()

    @api.multi
    def initialiser_dates(self):
        for job in self.env["hr.job"].search([]):
            job.date_cloture = job.create_date.date()

    @api.multi
    def unpublish_job(self):
        for job in self.env["hr.job"].search([]):
            if job.date_cloture:
                if job.date_cloture + timedelta(days=30) < (datetime.today()).date():
                    job.website_published = False


class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    sector_ids = fields.Many2many("hr.applicant_sector", relation="hr_applicant_sector_rel", string="Secteurs Associes")
    domaine_ids = fields.Many2many("hr.applicant_domaine", relation="hr_applicant_domaine_rel",
                                   string="Domaines Associes")

    langue_ids = fields.One2many(
        string='langues parlées',
        comodel_name='hr.applicant_language_relation',
        inverse_name='applicant_id',
        related='candidat_id.langue_ids',
        depends=['candidat_id'],
    )
    experience_ids = fields.One2many(
        string='Expériences Professionnelle',
        comodel_name='hr.applicant.experience',
        inverse_name='applicant_id',
        related='candidat_id.experience_ids',
        depends=['candidat_id'],
    )
    education_ids = fields.One2many(
        string='Education',
        comodel_name='hr.applicant.education',
        inverse_name='applicant_id',
        related='candidat_id.education_ids',
        depends=['candidat_id'],
    )
    formation_ids = fields.One2many(
        string='Formations',
        comodel_name='hr.applicant.formation',
        inverse_name='applicant_id',
        related='candidat_id.formation_ids',
        depends=['candidat_id'],
    )
    competence_ids = fields.One2many(
        string='Competences',
        comodel_name='hr.applicant_competence_relation',
        inverse_name='applicant_id',
        related='candidat_id.competence_ids',
        depends=['candidat_id'],
    )
    year_of_bac = fields.Date("Year of BAC")
    professional_training = fields.Text("Professional Training")
    reference_ids = fields.One2many(
        string='References',
        comodel_name='hr.applicant.reference',
        inverse_name='applicant_id',
    )
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Photo", default=_default_image, attachment=True,
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    candidat_id=fields.Many2one(string="Candidat",comodel_name="hr.applicant.candidate")

    @api.depends("partner_name")
    def _onchange_attachment_ids(self):
        for app in self:
            read_group_res = self.env['ir.attachment'].read_group(
                [('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.ids)],
                ['res_id'], ['res_id'])
            print("************attachment*********")
            print(read_group_res)
            print("************attachment*********")
            """for attach in app.attachment_ids:
                if attach.mimetype in ["image/png","image/jpeg","image/gif"]:
                    #app.image=attach.datas
                    pass"""

    @api.multi
    def write(self, vals):
        logging.info("==========================valeurs en ecriture ============================")
        logging.info(vals)
        tools.image_resize_images(vals)
        for app in self:
            app._onchange_attachment_ids()
        res = super(Applicant, self).write(vals)

        return res

    @api.model
    def notification_aplicant_creation(self, applicant):

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")
        logging.info("==========================application stage sequence ============================")
        logging.info(applicant.stage_id.sequence)
        logging.info(applicant.stage_id.name)
        if applicant.stage_id.name != "Not retained":
            if applicant:
                logging.info("==========================application ============================")
                logging.info(applicant)
                logging.info("==========================application name ============================")
                logging.info(applicant.name)
                logging.info("==========================application partner name ============================")
                logging.info(applicant.partner_name)
                logging.info("==========================application id ============================")
                logging.info(applicant.id)

                receivers_email1 = "arnold.bukasa1@gmail.com"
                logging.info("==========================application from email ============================")
                logging.info(applicant.email_from)

                if applicant.email_from:
                    x = applicant.email_from.split("<")
                    w = applicant.email_from
                    y = ""
                    if len(x) > 1:
                        y = x[1]
                        w = y.split(">")
                        z = w[0]
                    else:
                        z = w
                    receivers_email = str(z)
                    logging.info("==========================application email in ============================")
                    logging.info(receivers_email)
                    if applicant.partner_name:
                        Candidat = applicant.partner_name
                    elif applicant.email_from:
                        Candidat = applicant.email_from
                    else:
                        Candidat = "pas de nom"

                    message = MIMEMultipart('alternative')
                    message['To'] = receivers_email
                    message['CC'] = "recrutement@bensizwe.com"
                    message['Subject'] = "VOTRE CANDIDATURE BENSIZWE"

                    message_texte = str(
                        "Bonjour " + Candidat + ",<br>Nous accusons réception de votre candidature et nous vous remercions de l’intérêt que vous portez à la société Bensizwe.<br>Votre dossier sera traité dans les plus brefs délais.<br>Cependant, si vous n’avez pas de nouvelles de notre part dans les trois semaines qui suivent ce courrier, veuillez considérer que nous ne sommes pas en mesure de répondre favorablement à votre candidature.<br>Votre CV sera enregistré dans notre base de données pour des éventuelles opportunités d’embauche.<br><br>Nous vous prions d’agréer, Madame, Mademoiselle, Monsieur, nos salutations les meilleures.<br><br>DEPARTEMENT DE RECRUTEMENT BENSIZWE")

                    logging.info(
                        "========================== email candidat =============================================")
                    logging.info(receivers_email)

                    mt_html = MIMEText(message_texte, "html")
                    message.attach(mt_html)
                    server.sendmail("notification@bensizwe.com", receivers_email, message.as_string())

                    server.quit()

    @api.model
    def create(self, vals):
        logging.info("==========================valeurs en creation avant check============================")
        logging.info(vals["job_id"])
        if vals["job_id"] == False:

            job_id = self.env["hr.job"].search([('name', '=', 'Candidature par Mail')], limit=1)
            if job_id:
                vals["job_id"] = job_id.id

        elif vals["job_id"] == "":
            job_id = self.env["hr.job"].search([('name', '=', 'Candidature par Mail')], limit=1)
            if job_id:
                vals["job_id"] = job_id.id
        logging.info("==========================valeurs en creation apres check============================")
        logging.info(vals["job_id"])
        applicant = super(Applicant, self).create(vals)
        logging.info("==========================valeurs en creation ============================")
        logging.info(vals)
        if applicant.job_id:
            try:
                applicant.notification_aplicant_creation(applicant)
            except:
                logging.info("la connexion n est pas etablit")

        return applicant

    @api.multi
    def write(self, values):
        if "stage_id" in values:
            retained = self.env["hr.recruitment.stage"].search([("name", "=", "Not retained")], limit=1)
            logging.info("=========================== retained==================")
            logging.info(retained.id)
            logging.info("=========================== values==================")
            logging.info(values)

            if retained.id == values["stage_id"]:
                dup = self.copy(values)
                del values["stage_id"]
                logging.info("=========================== element crée==================")
                logging.info(dup)
                logging.info("=========================== values après création ==================")
                logging.info(values)
        res = super(Applicant, self).write(values)

        return res

    @api.one
    def copy(self, default):
        default = dict(default or {})

        return super(Applicant, self).copy(default)

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        super(Applicant, self).onchange_stage_id()
        logging.info("====================sate==========")
        logging.info(self.stage_id)
        logging.info(self.pool.get(self))
        state = self.env["hr.recruitment.stage"].search([("id", "=", self.stage_id.id)])
        logging.info("==================== sate sequence ==========")
        logging.info(self.stage_id.sequence)
        for applicant in self:
            if applicant.partner_name:
                Candidat = applicant.partner_name
            elif applicant.email_from:
                Candidat = applicant.email_from
            else:
                Candidat = "pas de nom"
            if applicant.job_id.name:
                poste = "de " + applicant.job_id.name
            else:
                poste = "sollicité"
            logging.info("========================== poste=============================================")
            logging.info(poste)

            email = applicant.email_from
            logging.info("========================== email =============================================")
            logging.info(applicant.name)
            logging.info(applicant)
            logging.info(applicant.email_from)
            to = email
            objet = "VOTRE CANDIDATURE BENSIZWE"
            cc = "recrutement@bensizwe.com"
            message_entretient1 = str(
                "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que vous êtes retenu pour une première interview au poste " + poste + ".<br>Un membre de notre équipe vous contactera pour vous communiquer le jour et l’heure de l’entrevue.<br>Bonne chance, ")
            message_entretient2 = str(
                "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que vous êtes retenu pour une deuxième interview au poste " + poste + ".<br>Un membre de notre équipe vous contactera pour vous communiquer le jour et l’heure de l’entrevue.<br>Bonne chance, ")
            message_test = str(
                "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que vous êtes retenu pour un Test au poste " + poste + ".<br>Un membre de notre équipe vous contactera pour vous communiquer le jour et l’heure de l’entrevue.<br>Bonne chance, ")
            message_not_retained = str(
                "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que votre candidature au poste " + poste + "n'a pas été retenu.<br>Cependant, nous n'hésiterons à vous tenir informé sur les prochaines opportunités correspondant à votre profil.<br>Merçi, ")

            if state.sequence == 2:
                messages = message_entretient1
                applicant.notification_standard(messages, email, objet, to, cc)
            elif state.sequence == 3:
                messages = message_entretient2
                applicant.notification_standard(messages, email, objet, to, cc)
            elif state.sequence == 6:
                messages = message_test
                applicant.notification_standard(messages, email, objet, to, cc)
            elif state.sequence == 7:
                messages = message_not_retained
                applicant.notification_standard(messages, email, objet, to, cc)

    @api.model
    def notification_standard(self, messages, email, objet, to, cc):

        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")
        receivers_email = email

        message = MIMEMultipart('alternative')
        message['To'] = to
        message['CC'] = cc
        message['Subject'] = objet
        message_texte = messages
        mt_html = MIMEText(message_texte, "html")
        message.attach(mt_html)
        server.sendmail("notification@bensizwe.com", email, message.as_string())
        server.quit()

    @api.model
    def notification_aplicant(self, etat, message):
        #    import smtplib
        logging.info("==========================Etat ============================")
        logging.info(etat)
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")

        for applicant in self:

            if applicant:
                logging.info("==========================application ============================")
                logging.info(applicant)
                logging.info("==========================application name ============================")
                logging.info(applicant.name)
                logging.info("==========================application partner name ============================")
                logging.info(applicant.partner_name)
                logging.info("==========================application id ============================")
                logging.info(applicant.id)

                receivers_email1 = "arnold.bukasa1@gmail.com"
                logging.info("==========================application from email ============================")
                logging.info(applicant.email_from)

                # if applicant:
                #    receivers_email2 ="arnold.bukasa1@gmail.com"
                if applicant.email_from:

                    receivers_email2 = applicant.email_from
                    logging.info("==========================application email in ============================")
                    logging.info(receivers_email2)
                    if applicant.partner_name:
                        Candidat = applicant.partner_name
                    elif applicant.email_from:
                        Candidat = applicant.email_from
                    else:
                        Candidat = "pas de nom"
                    if applicant.job_id.name:
                        poste = "de " + applicant.job_id.name
                    else:
                        poste = "sollicité"
                    logging.info("========================== poste=============================================")
                    logging.info(poste)

                    message = MIMEMultipart('alternative')
                    message['To'] = "recrutement@bensizwe.com"
                    message['CC'] = "recrutement@bensizwe.com"
                    message['Subject'] = "VOTRE CANDIDATURE BENSIZWE"

                    if etat == "Entretient 1":
                        message_texte = str(
                            "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que vous êtes retenu pour une première interview au poste " + poste + ".<br>Un membre de notre équipe vous contactera pour vous communiquer le jour et l’heure de l’entrevue.<br>Bonne chance, ")
                    elif etat == "Entretient 2":
                        message_texte = str(
                            "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que vous êtes retenu pour une deuxième interview au poste " + poste + ".<br>Un membre de notre équipe vous contactera pour vous communiquer le jour et l’heure de l’entrevue.<br>Bonne chance, ")
                    elif etat == "Test":
                        message_texte = str(
                            "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que vous êtes retenu pour un Test au poste " + poste + ".<br>Un membre de notre équipe vous contactera pour vous communiquer le jour et l’heure de l’entrevue.<br>Bonne chance, ")
                    elif etat == "Not retained":
                        message_texte = str(
                            "Bonjour " + Candidat + ",<br>Nous tenons à vous informer que votre candidature au " + poste + "n'a pas été retenu.<br>Cependant, nous n'hésiterons à vous tenir informer sur les prochaines opportunités correspondant à votre profil.<br>Merçi, ")

                    email1 = receivers_email2.split("<")
                    if len(email1) > 1:
                        email2 = str(email1[1])
                        email3 = email2.split(">")
                        emailfinal = str(email3[0])
                    else:
                        emailfinal = str(email1[0])
                    logging.info(
                        "========================== email candidat =============================================")
                    logging.info(emailfinal)

                    mt_html = MIMEText(message_texte, "html")
                    message.attach(mt_html)
                    server.sendmail("notification@bensizwe.com", emailfinal, message.as_string())

        server.quit()


class Application_sector(models.Model):
    _name = "hr.applicant_sector"
    _description = 'Secteurs d"activite'
    name = fields.Char(string="Secteur d'activité")


class Application_dommaine(models.Model):
    _name = "hr.applicant_domaine"
    _description = "Dommaine de compétence"
    name = fields.Char(string="Dommaine de compétence")


class Application_language(models.Model):
    _name = "hr.applicant_language"
    _description = "Langue Parlée"

    name = fields.Char(string="Langue Parlée")


class Application_Language(models.Model):
    _name = "hr.applicant_language_relation"

    name = fields.Char(string="Langue",compute="_default_langue_name", store=True)
    applicant_id = fields.Many2one("hr.applicant", string="Application")
    language_id = fields.Many2one("hr.applicant_language", string="Language")
    level = fields.Integer(string="Level")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")

    @api.depends("language_id")
    def _default_langue_name(self):
        logging.info("...")
        self.name="ma langue"

class Application_competence(models.Model):
    _name = "hr.applicant_comptence"
    _description = "Domaines de competence"

    name = fields.Char(string="Domaine de competence")


class Application_Competence(models.Model):
    _name = "hr.applicant_competence_relation"

    name = fields.Char(string="Competence")
    applicant_id = fields.Many2one("hr.applicant", string="Application")
    competence_id = fields.Many2one("hr.applicant_domaine", string="Domaine de Competence")
    level = fields.Integer(string="Level")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")

    @api.depends("competence_id")
    def _default_langue_name(self):
        logging.info("...")
        #self.name = self.competence_id.name

class Application_Sector(models.Model):
    _name = "hr.applicant_sector_rel"
    rec_name = "sector_id"

    applicant_id = fields.Many2one("hr.applicant", string="Application")
    sector_id = fields.Many2one("hr.applicant_sector", string="Sector")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")


class Application_Domaine(models.Model):
    _name = "hr.applicant_domaine_rel"

    name = fields.Char(string="Detail")
    applicant_id = fields.Many2one("hr.applicant", string="Application")
    domaine_id = fields.Many2one("hr.applicant_domaine", string="Domaine")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")


class ApplicantExperienceEntreprise(models.Model):
    _name = "hr.applicant.experience.entreprise"
    _description = "Entreprise"

    name = fields.Char(string="Nom de l'entreprise")


class ApplicantExperience(models.Model):
    _name = "hr.applicant.experience"
    _description = "Experience professionnelle"

    name = fields.Char(string="Detail du Poste")
    entreprise_id = fields.Many2one(
        string='Entreprise',
        comodel_name='hr.applicant.experience.entreprise',
        ondelete='restrict',
    )
    categorie_id = fields.Many2one(string="Secteur", comodel_name="hr.applicant_sector")
    sous_categorie_id = fields.Many2one(string="categogie", comodel_name="hr.applicant_domaine")
    date_debut = fields.Date(string="Date de debut")
    date_fin = fields.Date(string="Date de fin")
    taches = fields.Text(string="Taches effectuées")
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Candidature consernée")
    reference = fields.Char(string="Personne de reference")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")


class ApplicantEducation(models.Model):
    _name = "hr.applicant.education"
    _description = "Education"

    name = fields.Char(string="Domaine d'etude")
    institution = fields.Char(string='Institution', )
    date_debut = fields.Date(string="Date de debut")
    date_fin = fields.Date(string="Date de fin")
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Candidature consernée")
    qualification = fields.Char(string="Qualification")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")


class ApplicantFormation(models.Model):
    _name = "hr.applicant.formation"
    _description = "Formation"

    name = fields.Char(string="Domaine de formation")
    institution = fields.Char(string='Institution', )
    date_debut = fields.Date(string="Date de debut")
    date_fin = fields.Date(string="Date de fin")
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Candidature consernée")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")
    qualification = fields.Char(string="Qualification")


class ApplicantReference(models.Model):
    _name = "hr.applicant.reference"
    _description = "Personne de Réference"

    name = fields.Char(string="Nom")
    position = fields.Char(string='Position')
    telephone = fields.Char(string="Téléphone")
    entreprise_id = fields.Many2one(comodel_name="hr.applicant.experience.entreprise", string="Entreprise")
    applicant_id = fields.Many2one(comodel_name="hr.applicant", string="Candidature consernée")
    candidat_id = fields.Many2one(comodel_name="hr.applicant.candidate", string="Candidate")


class Candidate(models.Model):
    _name = "hr.applicant.candidate"
    _description = "Profil candidat"

    name = fields.Char(string="Nom du candidat")
    postnom = fields.Char(string="Postom du candidat")
    prenom = fields.Char(string="Prenom du candidat")
    age = fields.Integer(string="Age")
    annee_naissance = fields.Char(string="Année de naissance")
    adresse = fields.Char(string="Adresse Physique")
    ville = fields.Char(string="Ville")
    email=fields.Char(string="Email")
    password=fields.Char(string="Password")
    langue_ids = fields.One2many(
        string='langues parlées',
        comodel_name='hr.applicant_language_relation',
        inverse_name='candidat_id',
    )
    experience_ids = fields.One2many(
        string='Expériences Professionnelle',
        comodel_name='hr.applicant.experience',
        inverse_name='candidat_id',
    )
    education_ids = fields.One2many(
        string='Education',
        comodel_name='hr.applicant.education',
        inverse_name='candidat_id',
    )
    formation_ids = fields.One2many(
        string='Formations',
        comodel_name='hr.applicant.formation',
        inverse_name='candidat_id',
    )
    competence_ids = fields.One2many(
        string='Competences',
        comodel_name='hr.applicant_competence_relation',
        inverse_name='candidat_id',
    )
    year_of_bac = fields.Date("Year of BAC")
    professional_training = fields.Text("Professional Training")
    reference_ids = fields.One2many(
        string='References',
        comodel_name='hr.applicant.reference',
        inverse_name='candidat_id',
    )
    user_id=fields.Many2one(string="Utilisateur", comodel_name="res.users")