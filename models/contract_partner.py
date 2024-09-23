# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

class Partner_Contract(models.Model):
    _name = "partner.contract"
    _description = "Contracts des Clients"
    
    name=fields.Char(string="Description du contrat")
    datedebut=fields.Date(string="Date du debut initiale",default=fields.Date.today())
    datefin=fields.Date(string="Date de fin")
    cout=fields.Float(string="Coût du Contrat")
    department_id= fields.Many2one(string="Département en charge",  comodel_name="hr.department",domain=[('company_id.name', '=', 'Head Office')])
    partner=fields.Many2one(string="Client",comodel_name="partner.partner")
    employe_encharge=fields.Many2one(string="Employé en charge",  comodel_name="hr.employee",domain=[('company_id.name', '=', 'Head Office')])
    impacte_nr = fields.Html(string='Impact du non renouvelement')
    motifs_nr = fields.Html(string='Motifs du non renouvelement')
    clause_sortie = fields.Html(string='Clause de Sortie du contrat')
    state = fields.Selection( string="Etat",selection=[('draft', 'Brouillon'), ('encours', 'En cours'), ('renouvele', 'Rénouvelé'), ('cloture', 'Clotûré')],default="draft")
    prestation_ids= fields.One2many(string='Contrat',comodel_name='partner.prestation',inverse_name='contract_id')
    
    @api.model
    def create(self, vals):
        # Agregar codigo de validacion aca
        contrat = super(Partner_Contract, self).create(vals)
        if "partner" in vals: 
            contrat.name="Contrat de "+str(contrat.partner.name)
        return contrat
    
    @api.multi
    def action_confirm(self):
        for record in self:
            record.write( { 'state': 'encours'})
        return True
    @api.multi
    def action_close(self):
        for record in self:
            record.write( { 'state': 'cloture'})
        return True
    @api.multi
    def action_cancel(self):
        for record in self:
            record.write( { 'state': 'draft'})
        return True
    
    
class Prestation(models.Model):
    _name = "partner.prestation"
    _description = "Prestaion dans le contrat"
    
    name=fields.Char(string="Description")
    datedebut=fields.Date(string="Date du debut",default=fields.Date.today())
    datefin=fields.Date(string="Date de fin")
    state = fields.Selection( string="Etat",selection=[('encours', 'En cours'),('cloture', 'Clotûré')],default="encours")
    contract_id= fields.Many2one( string="Contrat",comodel_name="partner.contract", help="Le contrat du conserné.",)
    partner=fields.Many2one(string="Client",related='contract_id.partner', comodel_name="partner.partner", depends=['contract_id'] ,store=True)

class Partner(models.Model):
    _name = "partner.partner"
    _description="Client"
    
    name = fields.Char(string="Dénomination du Client")
    contact= fields.Char(string="Téléphone")
    email= fields.Char(string="Email")
    partner_contract_id= fields.One2many( string="Contrat",comodel_name="partner.contract", inverse_name="partner", help="Le contrat du client." )
    #prestation_ids= fields.One2many(related='partner_contract_id.prestation_ids',depends=['partner_contract_id'], string='prestations',store=True,readonly=True )  

