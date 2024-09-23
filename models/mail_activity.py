# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging


class ActivityStage(models.Model):
    _name = 'activity.stage'
    _inherit = ['mail.thread']
    _description = 'Stage d"activité'
    
    name=fields.Char(string="Stage")
    sequence=fields.Integer(string="Sequence")


class MailActivity(models.Model):
    _inherit = 'mail.activity'
     
    @api.model
    def _default_stage(self):
        stage= self.env["activity.stage"].search([("name","=","Affectée")]).id or False
        return stage
      
    #ticket_id = fields.Many2one(string='Ticket', comodel_name='escalator_lite.ticket',)
    stage_id= fields.Many2one(string='Stage', comodel_name='activity.stage',default=_default_stage)
    
    

    @api.model
    def create(self, vals):
        # Agregar codigo de validacion aca
        activite=super(MailActivity, self.sudo()).create(vals)
        activite.notifier()     
        #activite.creer_ticket()
        
        
        return activite
    
    @api.model
    def notifier(self):
        for activite in self.sudo():
            logging.info("======================== le model =============================")
            logging.info(activite.res_model_id.model ) 
            
            if activite.res_model_id.model in  ["crm.lead"]:
            
                act_resume= activite.summary
                act_deadline = activite.date_deadline
                act_creator= activite.create_user_id
                act_assigned_to =activite.user_id
                nom_destinateur=activite.user_id.employee_id.name or ""
                nom_createur=activite.create_user_id.employee_id.name or activite.create_uid.name
                titre= activite.res_name or activite.summary 
                deadline=str(act_deadline) or ""
                logging.info("======================== deadline=============================")
                logging.info(act_deadline) 
                logging.info("======================== createur=============================")
                logging.info(act_creator.employee_id.name)
                logging.info("======================== Assigné à =============================")
                logging.info(act_assigned_to.employee_id.name)
                
                message_texte=str("Hi "+nom_destinateur +"!<br> the system generated a new Task and ticket, The CRM process need your action, the task has been created from the opportunity: "+activite.res_name+" and the deadline date is :"+ deadline+",<br> Please login if the Task is done and mark is done")
                    
                server = smtplib.SMTP('smtp.office365.com', 587)
                server.starttls()
                server.login("notification@bensizwe.com", "Fug42481")
                logging.info("======================== notification ticket =============================")
                logging.info(self)       
                logging.info("======================== user assigned to =============================")
                logging.info(act_assigned_to.employee_id.name)
                message= MIMEMultipart('alternative')
                message['To'] = act_assigned_to.employee_id.work_email
                message['CC'] = act_assigned_to.employee_id.work_email
                message['Subject'] = "CRM NEW TASK ASSIGNATION ("+titre+")"  
                            
                mt_html = MIMEText(message_texte, "html")
                message.attach(mt_html)
                server.sendmail("notification@bensizwe.com", act_assigned_to.employee_id.work_email, message.as_string())
            
""" @api.model
    def creer_ticket(self):
        for activite in self:
            
            name= activite.summary
            date_deadline = activite.date_deadline
            employee_id= activite.user_id.employee_id.id or False
            user_id =activite.user_id.id
            description=activite.note
            vals={
                "name":name,
                "description":description,
                "employee_id":employee_id,
                "user_id":user_id,
                "date_deadline":date_deadline,
                #"expense_sheet_id":expense.id,
                "color":4,
                }
            ticket= self.env["escalator_lite.ticket"].create(vals)
            activite.ticket_id=ticket.id
            logging.info("======================== Ticket crée =============================")
            logging.info(ticket)"""