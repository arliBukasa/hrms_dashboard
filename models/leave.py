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
from math import *

class HolidaysRequest(models.Model):
    
    _inherit="hr.leave"
    number_of_days_display = fields.Float( precision_digits=1)
    number_of_days_reste = fields.Float( precision_digits=1, string="Nombre des Jours restants" )
    
    @api.model
    def notification_standard(self,messages,email,objet,to,cc):
        logging.info("=======================================valeurs dans la fonction standar %s %s %s %s %s %s ",self,messages,email,objet,to,cc)  
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")
        receivers_email = email           
        
        message= MIMEMultipart('alternative')
        message['To'] = to
        message['CC'] = cc
        message['Subject'] = objet
        message_texte = messages
        logging.info("======== message : %s",messages)
        mt_html = MIMEText(message_texte, "html")
        message.attach(mt_html)
        server.sendmail("notification@bensizwe.com", email, message.as_string())
        server.quit()
        
    def _notify(self, state):
        """ notifications . """
        for holiday in self:
            objet="NOTIFICATION LEAVE REQUEST"
            manager=holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
            manager_email=manager.work_email
            manager_name = manager.name
            employee=holiday.employee_id
            employee_name=employee.name
            employee_email=employee.work_email
            hr=self.env["hr.department"].sudo().search([('name', '=', 'HUMAN RESSOURCES')],  limit=1)
            hr_email=hr.manager_id.work_email
            logging.info("================acteurs leave===========")
            logging.info(holiday)
            logging.info("======employee name and email======= name:%s email:%s",employee_name,employee_email)
            logging.info("======manager name and email======= name:%s email:%s",manager_name,manager_email)
            logging.info("======departement HR ======= :%s",hr)
            logging.info("======manager HR ======= :%s",hr.manager_id.name)
            logging.info("======manager HR email ======= :%s",hr_email)
            logging.info("======== state=====:%s",state)
            if state=="confirm":
                messages="Hi Dear Manager! <br> There is a leave request from "+employee_name+" please! follow this link to approve: https://apps.bzapps.ovh/web/login "
                holiday.notification_standard(messages,manager_email,objet,manager_email,employee_email)
            elif state == "validate1" :
                messages1="Hi Dear "+employee_name+"! <br> your leave request has been validated by your manager, it is being processed by Human resources"  
                messages2="Hi HR! <br> you have a leave request from "+employee_name+", validated by is manager which requires your approval please! follow this link to process: https://apps.bzapps.ovh/web/login "  
                holiday.notification_standard(messages1,employee_email,objet,employee_email,manager_email)
                if hr_email:
                    holiday.notification_standard(messages2,hr_email,objet,employee_email,manager_email)
            elif state=="validate" :
                messages1="Hi "+employee_name+"! <br> your leave request  has been validated by HR you can enjoy your holidays "  
                messages2="Hi "+manager_name+" !<br> the leave request from :"+employee_name+" has been validated by Hr " 
                holiday.notification_standard(messages1,employee_email,objet,employee_email,manager_email)
                holiday.notification_standard(messages2,manager_email,objet,manager_email,employee_email)
    @api.multi            
    def _auto_notify(self):
        """ notifications automatique . """
        
        for holiday in self.env["hr.leave"].search([('request_date_from', '=',(datetime.today()+timedelta(days=2)).date()),('state', '=',"validate")]):
            logging.info("================comapraison des leave:===========")
            logging.info((holiday.request_date_from==(datetime.today()+timedelta(days=1)).date()) and (holiday.state=="validate"))
            logging.info("================date de debut congé: %s===========",holiday.request_date_from)
            logging.info("================Aujourdhui: %s===========",(datetime.today()+timedelta(days=1)).date())
            logging.info("================etat: %s===========",holiday.state)
            #if (holiday.request_date_from==datetime.today()) and (holiday.state=="validate"):
            objet="NOTIFICATION LEAVE START"
            manager=holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
            manager_email=manager.work_email
            manager_name = manager.name
            employee=holiday.employee_id
            employee_name=employee.name
            employee_email=employee.work_email
            hr_manager=self.env["hr.department"].sudo().search([('name', '=', 'HUMAN RESSOURCES')],  limit=1)
           
            logging.info("================acteurs leave===========")
            logging.info(holiday)
            logging.info("======employee name and email======= name:%s email:%s",employee_name,employee_email)
            logging.info("======manager name and email======= name:%s email:%s",manager_name,manager_email)
            logging.info("======manager HR ======= Hr manager:%s",hr_manager)
            hr_email=hr_manager.manager_id.work_email
            if hr_email:
                logging.info("======Hr manager email ======= email:%s",self.env["hr.department"].sudo().search([('name', '=', 'HUMAN RESSOURCES')],  limit=1))
                
            messages1="Hi HR! <br> agent "+employee_name +"'s leave must start in 2 days , please! follow this link to see: https://apps.bzapps.ovh/web/login " 
            messages2="Hi "+employee_name  +" ! <br> your leave must start in 2 days"
            messages3="Hi "+manager_name+" !<br>agent "+employee_name+"'s leave must start in 2 days , please! follow this link to see: https://apps.bzapps.ovh/web/login "
            holiday.notification_standard(messages2,employee_email,objet,employee_email,manager_email)
            holiday.notification_standard(messages3,manager_email,objet,manager_email,employee_email)
            if hr_email:
                holiday.notification_standard(messages1,hr_email,objet,employee_email,manager_email)
    
    @api.multi
    def action_calculer_reste(self):
        for record in self:
            reste=0
            restes=0
            domain=[('allocation_type', 'in', ('no', 'fixed'))]
            leave_type=self.env['hr.leave.type'].search(domain)
            les_allocations = self.env["hr.leave.allocation"].search([('holiday_status_id', 'in', leave_type.ids),('employee_id', '=', record.employee_id.id),('state', '=', 'validate')])
            logging.info('Les allocations: %s',les_allocations)
            cumul =0.0
            for allocation in les_allocations:
                cumul = cumul+allocation.number_of_days
                logging.info('Le cumule: %s',cumul)
            logging.info('Le nombre des jours demandé: %s',record.number_of_days)
            for leave in self.env["hr.leave"].search([('holiday_status_id', 'in', leave_type.ids),('employee_id', '=', record.employee_id.id),('state', '=', 'validate')]):
                
                leave.write({"number_of_days_reste":0.0})
                restes=restes+leave.number_of_days 
                 
                logging.info('Le leave: %s',leave)
                logging.info('Le leave nombre jours: %s',leave.number_of_days)  
                logging.info('Le leave nombre jours restant: %s',leave.number_of_days_reste)        
            reste=cumul-restes
            record.write({"number_of_days_reste":reste })   
            logging.info('Le reste: %s',reste)
            logging.info('Le reste dans le record actuel: %s',record.number_of_days_reste)
    @api.multi
    def action_validate(self):
        logging.info("================je suis dans valider congé===========")
        super(HolidaysRequest, self).action_validate()
        self._notify("validate")
        self.action_calculer_reste()
       
    @api.multi
    def action_confirm(self):
        logging.info("================je suis dans confirm congé===========")
        super(HolidaysRequest, self).action_confirm()
        self._notify("confirm")
    @api.multi
    def action_approve(self):
        logging.info("================je suis dans approuver congé===========")
        super(HolidaysRequest, self).action_approve()
        self._notify('validate1')

    @api.model
    def create(self, values):
        result = super().create(values)
        if result.state=="confirm":
            result._notify("confirm")
        return result
    
    @api.multi
    @api.depends('number_of_days')
    def _compute_number_of_days_display(self):
        
        super(HolidaysRequest, self)._compute_number_of_days_display()
        
        for holiday in self:
            holiday.number_of_days_display = ceil(holiday.number_of_days)
            
class HolidaysAllocation(models.Model):

    _inherit = "hr.leave.allocation"
    
    @api.multi
    def write(self, values):
        res = super().write(values)
        if "state" in values:
            if values["state"] == "validate":                
                leave= self.env["hr.leave"].search([('employee_id', '=', self.employee_id.id)], limit=1)
                leave.action_calculer_reste()
        return res
        