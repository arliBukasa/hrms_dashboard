# -*- coding: utf-8 -*-
import base64
import calendar
import logging
import smtplib
import time
from calendar import weekday
from cgi import log
from collections import defaultdict
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.modules.module import get_module_resource
from odoo.tools import float_utils
from pytz import utc

class Casual(models.Model):
    _name="hrms.casual"
    
    name=fields.Char(string="Nom du Candidat")
    partner_mobile =fields.Char(string="Téléphone")
    adresse=fields.Char(string="Adresse Physique")
    email_from=fields.Char(string="Adresse email")
    
class Casual_Position(models.Model):
    _name="hrms.casual.position"
    _description="Job Position"
    
    name=fields.Char(string="Détail du poste")
    
class Recrutement(models.Model):
    _name="hrms.casual.recrutement"
    
    name = fields.Char(string="Description")
    date_debut=fields.Date(string="Date de debut")
    date_fin=fields.Date(string="Date de fin")
    position_id=fields.Many2one("hrms.casual.position",string="job position")
    client_id=fields.Many2one("hr.department", string="Client")
    lieu=fields.Char(string="Lieu d'affectation")
    responsable=fields.Char(string="Responsable du lieu")
    remuneration=fields.Float(string="Rémunération journalière")
    remuneration_totale=fields.Float(string="Rémunération Totale", 
        compute='_compute_remuneration' )
    province=fields.Char(string="Province")
    line_ids= fields.One2many('hrms.casual.recrutementline', 'recrutement_id', string="liste de recrutement")
    nombre_jours=fields.Integer(string="Nombre des jours")
    
    @api.depends('remuneration','nombre_jours')
    def _compute_remuneration(self):
        for record in self:
            record.remuneration_totale = record.remuneration*record.nombre_jours
            
class Recrutement_line(models.Model):
    _name="hrms.casual.recrutementline"
    _description="informations sur le candidat"
        
    casual_id = fields.Many2one('hrms.casual',string="Candidat")
    recrutement_id=fields.Many2one("hrms.casual.recrutement", string="Recrutement")
    date_debut=fields.Date(related='recrutement_id.date_debut', depends=['recrutement_id'], readonly=True,store=True)
    date_fin=fields.Date(related='recrutement_id.date_fin', depends=['recrutement_id'], readonly=True,store=True)
    position_id=fields.Many2one(related='recrutement_id.position_id', depends=['recrutement_id'], readonly=True,store=True)
    province=fields.Char(related='recrutement_id.province', depends=['recrutement_id'], readonly=True,store=True)
    client_id=fields.Many2one(related='recrutement_id.client_id', depends=['recrutement_id'], readonly=True,store=True)
    lieu=fields.Char(related='recrutement_id.lieu', depends=['recrutement_id'], readonly=True,store=True)
    responsable=fields.Char(related='recrutement_id.responsable', depends=['recrutement_id'], readonly=True,store=True)
    remuneration_totale=fields.Float(related='recrutement_id.remuneration_totale', depends=['recrutement_id'], readonly=True,store=True)
    nombre_jours=fields.Integer(related='recrutement_id.nombre_jours', depends=['recrutement_id'], readonly=True,store=True)  