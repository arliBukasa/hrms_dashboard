# -*- coding: utf-8 -*-
import base64
import calendar
import logging
import re
import smtplib
import time
from calendar import weekday
from cgi import log
from collections import defaultdict
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.modules.module import get_module_resource
from odoo.tools import float_utils
from pytz import utc

ROUNDING_FACTOR = 16


class Employee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date('Date of Birth', groups="base.group_user")
    heurs_prestations=fields.One2many("hr.timesheet.heuresimports","employee_id", string="Heures prestées") 
    numero_matricule=fields.Char(string="Numéro Matricule")
    adresse=fields.Char(string="Lieu de residence/ adresse Complet")
    ville=fields.Char(string="Ville")
    num_passeport=fields.Char(string="Numéro passeport")
    pere=fields.Char(string="Nom du père")
    mere=fields.Char(string="Nom de la mère")
    num_cnss=fields.Char(string="Numéro CNSS")   
    @api.model
    def get_user_employee_details(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        leaves_to_approve = self.env['hr.leave'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        today =datetime.strftime(datetime.today(), '%Y-%m-%d')
        
        query = """
        select count(id)
        from hr_leave
        WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s') and 
        state='validate'""" % (today, today)
        cr = self._cr
        cr.execute(query)
        leaves_today = cr.fetchall()
        first_day = date.today().replace(day=1)
        last_day = (date.today() + relativedelta(months=1, day=1)) - timedelta(1)
        query = """
                select count(id)
                from hr_leave
                WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s')
                and  state='validate'""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        leaves_this_month = cr.fetchall()
        leaves_alloc_req = self.env['hr.leave.allocation'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        timesheet_count = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False), ('user_id', '=', uid)])
        timesheet_view_id = self.env.ref('hr_timesheet.hr_timesheet_line_search')
        job_applications = self.env['hr.applicant'].sudo().search_count([])
        if employee:
            sql = """select broad_factor from hr_employee_broad_factor where id =%s"""
            self.env.cr.execute(sql, (employee[0]['id'],))
            result = self.env.cr.dictfetchall()
            broad_factor = result[0]['broad_factor']
            if employee[0]['birthday']:
                diff = relativedelta(datetime.today(), employee[0]['birthday'])
                age = diff.years
            else:
                age = False
            if employee[0]['joining_date']:
                diff = relativedelta(datetime.today(), employee[0]['joining_date'])
                years = diff.years
                months = diff.months
                days = diff.days
                experience = '{} years {} months {} days'.format(years, months, days)
            else:
                experience = False
            if employee:
                data = {
                    'broad_factor': broad_factor if broad_factor else 0,
                    'leaves_to_approve': leaves_to_approve,
                    'leaves_today': leaves_today,
                    'leaves_this_month':leaves_this_month,
                    'leaves_alloc_req': leaves_alloc_req,
                    'emp_timesheets': timesheet_count,
                    'job_applications': job_applications,
                    'timesheet_view_id': timesheet_view_id,
                    'experience': experience,
                    'age': age
                }
                employee[0].update(data)
            return employee
        else:
            return False

    @api.model
    def get_upcoming(self):
        cr = self._cr
        uid = request.session.uid
        employee = self.env['hr.employee'].search([('user_id', '=', uid)], limit=1)

        cr.execute("""select *, 
        (to_char(dob,'ddd')::int-to_char(now(),'ddd')::int+total_days)%total_days as dif
        from (select he.id, he.name, to_char(he.birthday, 'Month dd') as birthday,
        hj.name as job_id , he.birthday as dob,
        (to_char((to_char(now(),'yyyy')||'-12-31')::date,'ddd')::int) as total_days
        FROM hr_employee he
        join hr_job hj
        on hj.id = he.job_id
        ) birth
        where (to_char(dob,'ddd')::int-to_char(now(),'DDD')::int+total_days)%total_days between 0 and 15
        order by dif;""")
        birthday = cr.fetchall()
        cr.execute("""select e.name, e.date_begin, e.date_end, rc.name as location , e.is_online 
        from event_event e
        left join res_partner rp
        on e.address_id = rp.id
        left join res_country rc
        on rc.id = rp.country_id
        where e.state ='confirm'
        and (e.date_begin >= now()
        and e.date_begin <= now() + interval '15 day')
        or (e.date_end >= now()
        and e.date_end <= now() + interval '15 day')
        order by e.date_begin """)
        event = cr.fetchall()
        announcement = []
        if employee:
            department = employee.department_id
            job_id = employee.job_id
            sql = """select ha.name, ha.announcement_reason
            from hr_announcement ha
            left join hr_employee_announcements hea
            on hea.announcement = ha.id
            left join hr_department_announcements hda
            on hda.announcement = ha.id
            left join hr_job_position_announcements hpa
            on hpa.announcement = ha.id
            where ha.state = 'approved' and 
            ha.date_start <= now()::date and
            ha.date_end >= now()::date and
            (ha.is_announcement = True or
            (ha.is_announcement = False
            and ha.announcement_type = 'employee'
            and hea.employee = %s)""" % employee.id
            if department:
                sql += """ or
                (ha.is_announcement = False and
                ha.announcement_type = 'department'
                and hda.department = %s)""" % department.id
            if job_id:
                sql += """ or
                (ha.is_announcement = False and
                ha.announcement_type = 'job_position'
                and hpa.job_position = %s)""" % job_id.id
            sql += ')'
            cr.execute(sql)
            announcement = cr.fetchall()
        return {
            'birthday': birthday,
            'event': event,
            'announcement': announcement
        }

    @api.model
    def get_dept_employee(self):
        cr = self._cr
        cr.execute("""select department_id, hr_department.name,count(*) 
    from hr_employee join hr_department on hr_department.id=hr_employee.department_id 
    group by hr_employee.department_id,hr_department.name""")
        dat = cr.fetchall()
        data = []
        for i in range(0, len(dat)):
            data.append({'label': dat[i][1], 'value': dat[i][2]})
        return data
    @api.multi
    def _archiver(self):
        for employer in self.env["hr.employee"].search([("active","=",True)]):
            logging.info("============================ employer et contrat ==========================")
            logging.info(employer.name)
            if employer.contract_id:
                logging.info("============================ employer et contrat ==========================")
                logging.info(employer.name)
                logging.info(employer.contract_id)
                logging.info("============================ contrat  etat==========================")
                logging.info(employer.contract_id.state)
                if employer.contract_id.state == "close":
                    employer.write({"active":False})
                    body = "Fin de Contrat! Archivé par le système"

                    records = self._get_followers()
                    #followers = records[3[0]]['message_follower_ids']

                    self.message_post(body=body, subtype='mt_comment', partner_ids=records)
            else:
                employer.write({"active":False})
                body = "Fin de Contrat! Archivé par le système"
                records = self._get_followers()
                #followers = records[3[0]]['message_follower_ids']

                self.message_post( body=body, subtype='mt_comment', partner_ids=records)
    # @api.model
    # def get_broad_factor(self):
    #     emp_broad_factor = []
    #     sql = """select * from hr_employee_broad_factor"""
    #     self.env.cr.execute(sql)
    #     results = self.env.cr.dictfetchall()
    #     for data in results:
    #         broad_factor = data['broad_factor'] if data['broad_factor'] else 0
    #         if data['broad_factor']:
    #             vals = {
    #                 'id': data['id'],
    #                 'name': data['name'],
    #                 'broad_factor': broad_factor
    #             }
    #             emp_broad_factor.append(vals)
    #     return emp_broad_factor

    @api.model
    def get_department_leave(self):
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        self.env.cr.execute("""select id, name from hr_department""")
        departments = self.env.cr.dictfetchall()
        department_list = [x['name'] for x in departments]
        for month in month_list:
            leave = {}
            for dept in departments:
                leave[dept['name']] = 0
            vals = {
                'l_month': month,
                'leave': leave
            }
            graph_result.append(vals)
        sql = """
        SELECT h.id, h.employee_id,h.department_id
             , extract('month' FROM y)::int AS leave_month
             , to_char(y, 'Month YYYY') as month_year
             , GREATEST(y                    , h.date_from) AS date_from
             , LEAST   (y + interval '1 month', h.date_to)   AS date_to
        FROM  (select * from hr_leave where state = 'validate') h
             , generate_series(date_trunc('month', date_from::timestamp)
                             , date_trunc('month', date_to::timestamp)
                             , interval '1 month') y
        where date_trunc('month', GREATEST(y , h.date_from)) >= date_trunc('month', now()) - interval '6 month' and
        date_trunc('month', GREATEST(y , h.date_from)) <= date_trunc('month', now())
        and h.department_id is not null
        """
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        leave_lines = []
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'department': line['department_id'],
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month', 'department']).sum()
            result_lines = rf.to_dict('index')
            for month in month_list:
                for line in result_lines:
                    if month.replace(' ', '') == line[0].replace(' ', ''):
                        match = list(filter(lambda d: d['l_month'] in [month], graph_result))[0]['leave']
                        dept_name = self.env['hr.department'].browse(line[1]).name
                        if match:
                            match[dept_name] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + result['l_month'].split(' ')[1:2][0]
        return graph_result, department_list

    def get_work_days_dashboard(self, from_datetime, to_datetime, compute_leaves=False, calendar=None, domain=None):
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals(from_full, to_full, resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals:
            day_total[start.date()] += (stop - start).total_seconds() / 3600
        if compute_leaves:
            intervals = calendar._work_intervals(from_datetime, to_datetime, resource, domain)
        else:
            intervals = calendar._attendance_intervals(from_datetime, to_datetime, resource)
        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
            for day in day_hours
        )
        return days

    @api.model
    def employee_leave_trend(self):
        leave_lines = []
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        for month in month_list:
            vals = {
                'l_month': month,
                'leave': 0
            }
            graph_result.append(vals)
        sql = """
                SELECT h.id, h.employee_id
                     , extract('month' FROM y)::int AS leave_month
                     , to_char(y, 'Month YYYY') as month_year
                     , GREATEST(y                    , h.date_from) AS date_from
                     , LEAST   (y + interval '1 month', h.date_to)   AS date_to
                FROM  (select * from hr_leave where state = 'validate') h
                     , generate_series(date_trunc('month', date_from::timestamp)
                                     , date_trunc('month', date_to::timestamp)
                                     , interval '1 month') y
                where date_trunc('month', GREATEST(y , h.date_from)) >= date_trunc('month', now()) - interval '6 month' and
                date_trunc('month', GREATEST(y , h.date_from)) <= date_trunc('month', now())
                and h.employee_id = %s
                """
        self.env.cr.execute(sql, (employee[0]['id'],))
        results = self.env.cr.dictfetchall()
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month']).sum()
            result_lines = rf.to_dict('index')
            for line in result_lines:
                match = list(filter(lambda d: d['l_month'].replace(' ', '') == line.replace(' ', ''), graph_result))
                if match:
                    match[0]['leave'] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + result['l_month'].split(' ')[1:2][0]
        return graph_result

    @api.model
    def join_resign_trends(self):
        cr = self._cr
        month_list = []
        join_trend = []
        resign_trend = []
        for i in range(11, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            join_trend.append(vals)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            resign_trend.append(vals)
        cr.execute('''select to_char(joining_date, 'Month YYYY') as l_month, count(id) from hr_employee 
        WHERE joining_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month;''')
        join_data = cr.fetchall()
        cr.execute('''select to_char(resign_date, 'Month YYYY') as l_month, count(id) from hr_employee 
        WHERE resign_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month;''')
        resign_data = cr.fetchall()

        for line in join_data:
            match = list(filter(lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ', ''), join_trend))
            if match:
                match[0]['count'] = line[1]
        for line in resign_data:
            match = list(filter(lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ', ''), resign_trend))
            if match:
                match[0]['count'] = line[1]
        for join in join_trend:
            join['l_month'] = join['l_month'].split(' ')[:1][0].strip()[:3]
        for resign in resign_trend:
            resign['l_month'] = resign['l_month'].split(' ')[:1][0].strip()[:3]
        graph_result = [{
            'name': 'Join',
            'values': join_trend
        }, {
            'name': 'Resign',
            'values': resign_trend
        }]
        return graph_result

    @api.model
    def get_attrition_rate(self):
        month_attrition = []
        monthly_join_resign = self.join_resign_trends()
        month_join = monthly_join_resign[0]['values']
        month_resign = monthly_join_resign[1]['values']
        sql = """
        SELECT (date_trunc('month', CURRENT_DATE))::date - interval '1' month * s.a AS month_start
        FROM generate_series(0,11,1) AS s(a);"""
        self._cr.execute(sql)
        month_start_list = self._cr.fetchall()
        for month_date in month_start_list:
            self._cr.execute("""select count(id), to_char(date '%s', 'Month YYYY') as l_month from hr_employee
            where resign_date> date '%s' or resign_date is null and joining_date < date '%s'
            """ % (month_date[0], month_date[0], month_date[0],))
            month_emp = self._cr.fetchone()
            month_emp = (month_emp[0], month_emp[1].split(' ')[:1][0].strip()[:3])
            logging.info("============================ month ==========================")
            logging.info(month_emp)
            logging.info("============================ compare ==========================")
            logging.info((lambda d: d['l_month']))
            logging.info("============================ again ==========================")
            logging.info(month_emp[1].split(' ')[:1][0].strip()[:3])
            
            logging.info("============================ resign ==========================")
            logging.info(month_resign)
            logging.info("============================ filter ==========================")
            logging.info(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_resign))
            logging.info("============================ Liste ==========================")
            logging.info(list(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_resign)))
            
            
                              
                              
            match_join = list(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_join))
            match_resign =0# list(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_resign))#[0]['count']
            month_avg =0# (month_emp[0]+match_join-match_resign+month_emp[0])/2
            attrition_rate = (match_resign/month_avg)*100 if month_avg != 0 else 0
            vals = {
                # 'month': month_emp[1].split(' ')[:1][0].strip()[:3] + ' ' + month_emp[1].split(' ')[-1:][0],
                'month': month_emp[1].split(' ')[:1][0].strip()[:3],
                'attrition_rate': round(float(attrition_rate), 2)
            }
            month_attrition.append(vals)
        return month_attrition
    

    @api.multi
    def create(self, vals):
        #if "contract_id" not in vals:
           #raise UserError('Veuillez d"abord créer un contrat')
       
       
        return super(Employee ,self).create(vals) 
    
class Department(models.Model):

    _inherit = 'hr.department'
    
    name=fields.Char(string="CLient")
    contact=fields.Char(string="Contact du client")
    contrats_expirant= fields.Integer(string="Contrats Expirants", compute="_compute_expirants")
    contrats_encours= fields.Integer(string="Contrats Encours", compute="_compute_expirants")
    structure_id=fields.Many2one(string='Salary Structure',
        comodel_name='hr.payroll.structure',
        ondelete='restrict',)
    @api.multi
    def _compute_expirants(self):
       
        for department in self:
            employers=self.env["hr.employee"].search([("department_id","=",department.name)])
            contrats=0
            contrats_encours=0
            for employer in employers:
                if employer.contract_id.state == "pending":
                    contrats+=1
                if employer.contract_id.state in ["draft","open"]:
                    contrats_encours += 1
            department.contrats_expirant= contrats
            department.contrats_encours= contrats_encours
    
class Contract(models.Model):

    _inherit = 'hr.contract'
    
    hourly_rate_attendance = fields.Float(
        string="Hourly rate for attendance")
    logement = fields.Float(string="frais logement")
    transport = fields.Float(string="frais mensuel de transport",defaut=0)
    salaire_brute = fields.Float(string="salaire brut",)
    salaire_base = fields.Float(string="salaire de base")
    retenus = fields.Float(string="retenus")
    ipr=fields.Float(string="ipr")
    cnss=fields.Float(string="cnss")
    nombre_jours=fields.Float(string="Nombre des jours de prestation", default=22, required=True)
    struct_id=fields.Many2one(related='department_id.structure_id', depends=['department_id'], store=True, readonly=False
        )
    
    @api.onchange('department_id')
    def onchange_department_id(self):
        self.struct_id = self.department_id.structure_id or 1
    
    @api.multi
    def _cloturer_contrats(self):
        for contrat in self:
            contrat.write({"state":"close"})
    @api.multi
    def _marquer_arenouveler(self):
        for contrat in self:
            contrat.write({"state":"close"})
            
    @api.onchange('salaire_brute')
    def _onchange_salaire_brute(self):
                          
        brute_entre=self.salaire_brute
        reglages=self.env['hr.reglages'].search([])
        if reglages:
            for regl in reglages:
                if regl.struct_id==self.struct_id:
                    reglage= regl
                else:
                    reglage=self.env['hr.reglages'].search([("name","=",1)],limit=1)
    #===============================================================
        taux=reglage.taux
        baseT=0.0
        transport=0.0
        net=0.0
        loyer=reglage.taux_logement*baseT
        inss=reglage.taux_cnss*baseT
        ipr=0.0
        brute=0.0
        while (brute<brute_entre):
            logging.info("================== comparaison while externe ======================")
            logging.info((brute))
            logging.info(((brute_entre)))
            if ((brute)<=((brute_entre)/2)):
                logging.info("================== comparaison while ======================")
                logging.info((brute))
                logging.info(((brute_entre)/2))
                baseT+=baseT
                logging.info(baseT)
            elif (brute)<=((brute)/3):
                baseT+=baseT/3
                logging.info("================== comparaison while 2: ======================")
                logging.info((brute*taux))
                logging.info((brute)/3)
                
            baseT+=0.04
            loyer=reglage.taux_logement*baseT
            inss=reglage.taux_cnss*baseT          
            net=brute-(ipr/taux)-inss
            imposable=baseT-inss

            if ( (net<= 500)):
                transp= 50
            if (net>=501 and net<=750):
                transp= 100
            if (net>=751 and net<=1000):     
                transp= 150
            if (net>=1001 and net<=1500):
                transp= 200
            if (net>=1501):
                transp= 250
            if self.transport==0:
                transport=transp
            else:
                transport=self.transport
                
            brute=baseT+loyer+transport
            logging.info("================== Imposable x taux: ======================")
            logging.info(imposable*taux)
            
            if(imposable*taux>3600001):
                ipr=((4860.0+ 245699.85 +539999.70)+(((imposable*taux)-3600001)*reglage.taux_pallier4))           
            elif (imposable*taux>1800001):
                ipr= ((4860.0+245699.85)+((imposable*taux)-1800001)*reglage.taux_pallier3)
            elif((imposable*taux)>162001):
                ipr= 4860.0+(((imposable*taux)-162001.00)*reglage.taux_pallier2)
            elif(imposable*taux<162001):
                ipr= imposable*taux*reglage.taux_pallier1
     
            net=brute-(ipr/taux)-inss
            logging.info("================== les valeurs qui varient: ======================")
            logging.info("ipr:")
            logging.info(ipr/taux)
            logging.info("inss:")
            logging.info(inss)
            logging.info("base taxable:")
            logging.info(baseT)
            logging.info("net:")
            logging.info(net)
            logging.info("imposable:")
            logging.info(imposable)
            logging.info("taux:")
            logging.info(taux)
            logging.info("base journaliere:")
            logging.info(baseT/self.nombre_jours)
            
        taxes=(ipr/taux)+inss    
        self.hourly_rate_attendance = ((baseT)/self.nombre_jours)/8.5
        self.transport = transport
        self.logement = loyer
        self.salaire_base = baseT
        self.wage = net
        self.retenus=taxes
        self.ipr=ipr/taux
        self.cnss=inss
    
    @api.onchange('wage')
    def _onchange_wage(self):
        logging.info("=====================comparaison==============")
        logging.info(self.salaire_brute==0.0)
        if (self.salaire_brute==0.0):
            
            if ( (self.wage <= 500)):
                transp= 50
            if (self.wage>=501 and self.wage<=750):
                transp= 100
            if (self.wage>=751 and self.wage<=1000):
                transp= 150
            if (self.wage>=1001 and self.wage<=1500):
                transp= 200
            if (self.wage>=1501):
                transp= 250
                
            if self.transport==0:
                transport=transp
            else:
                transport=self.transport
                
            net_entre=self.wage
            reglage=self.env['hr.reglages'].search([("name","=",1)],limit=1)
    #===============================================================
            taux=reglage.taux
            baseT=0.0
            loyer=reglage.taux_logement*baseT
            inss=reglage.taux_cnss*baseT
            
            brute=baseT+loyer+transp
            net=0.0
            ipr=0.0
            while (net<net_entre):
                if ((net*taux)<=((net_entre*taux)/2)):
                    logging.info("================== comparaison while ======================")
                    logging.info((net*taux))
                    logging.info(((net_entre*taux)/2))
                    baseT+=baseT
                    logging.info(baseT)
                elif (net*taux)<=((net_entre*taux)/3):
                    baseT+=baseT/3
                    logging.info("================== comparaison while 2: ======================")
                    logging.info((net*taux))
                    logging.info((net_entre*taux)/3)
                    
                baseT+=0.04
                loyer=reglage.taux_logement*baseT
                inss=reglage.taux_cnss*baseT
                brute=baseT+loyer+transport
                
                imposable=baseT-inss
                
                logging.info("================== Imposable des vue: ======================")
                logging.info(imposable*taux)
                
                if(imposable*taux>3600001):
                    ipr=((4860.0+ 245699.85 +539999.70)+(((imposable*taux)-3600001)*reglage.taux_pallier4))           
                elif (imposable*taux>1800001):
                    ipr= ((4860.0+245699.85)+((imposable*taux)-1800001)*reglage.taux_pallier3)
                elif((imposable*taux)>162001):
                    ipr= 4860.0+(((imposable*taux)-162001.00)*reglage.taux_pallier2)
                elif(imposable*taux<162001):
                    ipr= imposable*taux*reglage.taux_pallier1
        
                net=brute-(ipr/taux)-inss
                logging.info("================== les valeurs qui varient: ======================")
                logging.info("ipr:")
                logging.info(ipr/taux)
                logging.info("inss:")
                logging.info(inss)
                logging.info("base taxable:")
                logging.info(baseT)
                logging.info("net:")
                logging.info(net)
                logging.info("imposable:")
                logging.info(imposable)
                logging.info("taux:")
                logging.info(taux)
                logging.info("base journaliere:")
                logging.info(baseT/self.nombre_jours)
                
            taxes=(ipr/taux)+inss    
            self.hourly_rate_attendance = ((baseT)/self.nombre_jours)/8.5
            self.transport = transport
            self.logement = loyer
            self.salaire_base = baseT
            self.salaire_brute = brute
            self.retenus=taxes
            self.ipr=ipr/taux
            self.cnss=inss
    
    @api.multi    
    def cloturer_contrat(self):
        contrats = self.env['hr.contract'].search([])

        for contrat_encours in contrats:
            if contrat_encours.date_end:
                contrat_fin=fields.Datetime.from_string(contrat_encours.date_end)
                #contrat_fin=datetime.datetime(int(contrat_encours.date_end[0:4]),int(contrat_encours.date_end[5:7]),int(contrat_encours.date_end[8:10]))
                logging.info("================== date fin contrat : ======================")
                logging.info((contrat_fin).date())
                if ((contrat_fin).date()>=(datetime.now()).date()):
                    contrat_encours.write({'state':'open'})
                if ((contrat_fin).date()<(datetime.now()).date()):
                    
                    if (((contrat_fin+timedelta(days=10)).date())<((datetime.now().date()))):
                        contrat_encours.write({'state':'close'})
                    else:
                        contrat_encours.write({'state':'pending'})
                        
    @api.model
    def notification_fin_contrat(self):

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")
        
        
        for contrat in self.env['hr.contract'].search([]):
            receivers_email1 = "arcel@bensizwe.com"
            receivers_email2 = "arnold.bukasa1@gmail.com"
            receivers_email3 = "agnes@bensizwe.com"
            if (contrat.date_end):
                contrat_fin=fields.Datetime.from_string(contrat.date_end)
                #contrat_fin=datetime(int(contrat.date_end[0:4]),int(contrat.date_end[5:7]),int(contrat.date_end[8:10]))
                logging.info("================== date fin contrat : ======================")
                logging.info((contrat_fin).date())
                logging.info((datetime.now()-timedelta(days=10)).date())
                logging.info((contrat_fin).date()==(datetime.now()-timedelta(days=10)).date())
                if (((contrat_fin).date()==(datetime.now()-timedelta(days=10)).date())):
                                
                    agent=contrat.employee_id.name
                    job_position = contrat.employee_id.job_id.name
                    client= contrat.employee_id.department_id.name
                    responsable=contrat.employee_id.department_id.manager_id
                    message= MIMEMultipart('alternative')
                    message['To'] = receivers_email1
                    message['CC'] = "agnes@bensiswe.com"
                    message['Subject'] = "Notification fin Contract"
                    message_texte = str("bonjour HR, l agent "+agent+" ocuppant le poste "+job_position+" du client "+client+" sera fin contrat dans 10 jours")
                    mt_html = MIMEText(message_texte, "html")
                    message.attach(mt_html)
                    server.sendmail("notification@bensizwe.com", receivers_email1, message.as_string())
                    #server.sendmail("notification@bensizwe.com", receivers_email2, message.as_string())
                    server.sendmail("notification@bensizwe.com", receivers_email3, message.as_string())
                    if responsable:
                        reciever=responsable.work_email
                        if reciever:
                            message_texte = str("bonjour "+responsable.name+", l agent "+agent+" ocuppant le poste "+job_position+" du client "+client+" sera fin contrat dans 10 jours")
                            mt_html = MIMEText(message_texte, "html")
                            message.attach(mt_html)
                            server.sendmail("notification@bensizwe.com", reciever, message.as_string())
                            
        server.quit()
                        
class Reglagespaie(models.Model):
    _name="hr.reglages"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _descripton="réglages pour payroll"
    
    name=fields.Integer(string="numero du reglage", default=1)
    taux=fields.Float(string="Taux",default=1650)
    taux_cnss=fields.Float(string="Taux cnss", default=0.05)
    taux_anciennete=fields.Float(string="Taux Anciennete")
    taux_logement=fields.Float(string="Taux du logement", default=0.3)
    taux_pallier1=fields.Float(string="Taux pallier 1 (0-162000)", default=0.03)
    taux_pallier2=fields.Float(string="Taux pallier 2 (1800000-162001)", default=0.15)
    taux_pallier3=fields.Float(string="Taux pallier 3 (3600000-1800001)", default=0.3)
    taux_pallier4=fields.Float(string="Taux pallier 4 (>3600000)", default=0.4)
    struct_id = fields.Many2one(
        string='Salary Structure',
        comodel_name='hr.payroll.structure',
        ondelete='restrict',
    )
    
    @api.model
    def _appliquer(self):
        contracts = self.env['hr.contract'].search([])
        for contract in contracts:
            contract._onchange_wage()
    
class hr_timesheet_heures_importees (models.Model):
    _name="hr.timesheet.heuresimports"
    _description="Jours de prestation importees"
    
    client=fields.Many2one("hr.department", string="Client")
    employee_id=fields.Many2one("hr.employee", string="Les employees consernes")
    moi=fields.Selection([(1,"Janvier"),(2,"Fevrier"),(3,"Mars"),(4,"Avril"),(5,"Mai"),(6,"Juin"),(7,"Juillet"),(8,"Aout"),(9,"Septembre"),(10,"Octobre"),(11,"Novembre"),(10,"Decembre")],string="Moi conserne")
    annee=fields.Selection([(y, str(y)) for y in range(1970, (datetime.now().year + 30)+1 )],string="Année: ex. '2020'")
    nombre_jours=fields.Integer(string="Nombre des jours")
    heure_sup_R1=fields.Float(string="Heures suplémentaires Rate 1")
    heure_sup_R2=fields.Float(string="Heures suplémentaires Rate 2")
    heure_sup_R3=fields.Float(string="Heures suplémentaires Rate 3")
    heure_sup_Nuit=fields.Float(string="Heures de nuit")
    lot_id=fields.Many2one("hr.timesheet.lot", stirng="Lot conserne")
    autres_paiements=fields.Float(string="Autres Paiements")
    bonus_shop=fields.Float(string="Bonus Shop")
    bonus_call=fields.Float(string="Bonus call")
    oncall=fields.Float(string="On Call")
    variable_region=fields.Float(string="Variable region")
    
class hr_heures_suplementaires(models.Model):
    _name="hr_timesheet_sheet.heures_suplementaires"
    
    jour=fields.Selection([('lundi', 'Lundi'), ('mardi', 'Mardi'), ('mercredi', 'Mercredi'), ('jeudi', 'Jeudi'), ('vendredi', 'Vendredi'), ('samedi', 'Samedi'), ('dimanche', 'Dimanche')], 'Jour de la semaine') 
    date=fields.Date('Date de prestation')
    heure_debut=fields.Char('Heure de début')
    heure_fin=fields.Char('Heure de fin')
    nombre_heures=fields.Float('nombre d " heures')
    timesheet_id=fields.Many2one('hr_timesheet_sheet.sheet','feuille de temps')
    
    @api.onchange('heure_fin')
    def _onchange_heure_fin(self):
        
        if self.heure_debut:
            
            
            dateheuredebut=self.date+' '+self.heure_debut
            dateheurefin=self.date+' '+self.heure_fin

            debut=datetime.datetime(int(dateheuredebut[0:4]),int(dateheuredebut[5:7]),int(dateheuredebut[8:10]),int(dateheuredebut[11:13]),int(dateheuredebut[14:16]))
            fin=datetime.datetime(int(dateheurefin[0:4]),int(dateheurefin[5:7]),int(dateheurefin[8:10]),int(dateheurefin[11:13]),int(dateheurefin[14:16]))
            heurestravail=float(((fin - debut).total_seconds() / 3600.0))
            self.nombre_heures = heurestravail
            #self.timesheet_id.calcule_heures_suplementaire(self)
            
    @api.onchange('heure_debut')
    def _onchange_heure_debut(self):
        
        if self.heure_fin:
            dateheuredebut=self.date+' '+self.heure_debut
            dateheurefin=self.date+' '+self.heure_fin

            debut=datetime.datetime(int(dateheuredebut[0:4]),int(dateheuredebut[5:7]),int(dateheuredebut[8:10]),int(dateheuredebut[11:13]),int(dateheuredebut[14:16]))
            fin=datetime.datetime(int(dateheurefin[0:4]),int(dateheurefin[5:7]),int(dateheurefin[8:10]),int(dateheurefin[11:13]),int(dateheurefin[14:16]))
            heurestravail=float(((fin - debut).total_seconds() / 3600.0))
            self.nombre_heures = heurestravail
            #self.timesheet_id.calcule_heures_suplementaire(self)
class hr_timesheet_sheet(models.Model):

    _name = 'hr_timesheet_sheet.sheet'
    
    lot_id=fields.Many2one("hr.timesheet.lot", stirng="Lot conserne")    
    
class hr_timesheet_lot (models.Model):
    _name="hr.timesheet.lot"
    _description="lot des feuilles de temps"
    
    client=fields.Many2one("hr.department", string="Client")
    moi=fields.Selection([(1,"Janvier"),(2,"Fevrier"),(3,"Mars"),(4,"Avril"),(5,"Mai"),(6,"Juin"),(7,"Juillet"),(8,"Aout"),(9,"Septembre"),(10,"Octobre"),(11,"Novembre"),(10,"Decembre")],string="Moi conserne")
    annee=fields.Selection([(y, str(y)) for y in range(1970, (datetime.now().year + 30)+1 )],string="Année: ex. '2020'")
    nombre_jours=fields.Integer(string="Nombre des jours")
    name=fields.Char(string="Description")
    date_debut=fields.Date(string="Date de debut")
    date_fin=fields.Date(string="Date de fin")
    employee_ids=fields.Many2many("hr.employee",relation="lot", string="Les employees consernes")
    timesheet_ids = fields.One2many("hr.timesheet.heuresimports","lot_id", string="feuilles de temps")
    
    @api.multi
    def creer_lot(self):
        for employee in self.employee_ids:
            logging.info("=================  employee ===================================================")
            logging.info(employee.name)
            date_from=self.date_debut
            date_to=self.date_fin
            employee_id=employee.id
            user_id=employee.user_id.id
            state="draft"
            department_id=employee.department_id.id
            lot_id=self.id
            
            sheet=self.env["hr.timesheet.heuresimports"].create({"moi":self.moi,"annee":self.annee,"nombre_jours":self.nombre_jours,"employee_id":employee.id,"state":state,"client":self.client.id,"lot_id":self.id})

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    
    mois=fields.Selection([(1,"Janvier"),(2,"Fevrier"),(3,"Mars"),(4,"Avril"),(5,"Mai"),(6,"Juin"),(7,"Juillet"),(8,"Aout"),(9,"Septembre"),(10,"Octobre"),(11,"Novembre"),(10,"Decembre")],string="Moi conserne", required="True")
    annee=fields.Selection([(y, str(y)) for y in range(1970, (datetime.now().year + 30)+1 )],string="Année: ex. '2020'",required="True")
    
    heures_prestation=fields.Many2one("hr.timesheet.heuresimports", string="Heures prestées")
    nombre_jours=fields.Integer(string="Nombre des jours")
    heure_sup_R1=fields.Float(string="Heures suplémentaires Rate 1")
    heure_sup_R2=fields.Float(string="Heures suplémentaires Rate 2")
    heure_sup_R3=fields.Float(string="Heures suplémentaires Rate 3")
    heure_sup_Nuit=fields.Float(string="Heures de nuit")
    autres_paiements=fields.Float(string="Autres Paiements")
    autres_paiements=fields.Float(string="Autres Paiements")
    bonus_shop=fields.Float(string="Bonus Shop")
    bonus_call=fields.Float(string="Bonus call")
    oncall=fields.Float(string="On Call")
    variable_region=fields.Float(string="Variable region")
    salaire_net=fields.Float(string="Salaire Net", compute="_compute_paiement_values", default=0.0)
    salaire_brut=fields.Float(string="Salaire Brut" , compute="_compute_paiement_values", default=0.0)
    salaire_base=fields.Float(string="Salaire de Base" , compute="_compute_paiement_values", default=0.0)
    imposables=fields.Float(string="imposables" , compute="_compute_paiement_values", default=0.0)
    cnss=fields.Float(string="Cnss" , compute="_compute_paiement_values", default=0.0)
    ipr=fields.Float(string="Ipr" , compute="_compute_paiement_values", default=0.0)
    transport=fields.Float(string="Transport" , compute="_compute_paiement_values", default=0.0)
    logement=fields.Float(string="Logement" , compute="_compute_paiement_values", default=0.0)
    @api.model
    def compute_ipr(self,imposable):
        reglage=self.env['hr.reglages'].search([("name","=",1)],limit=1)
        taux =reglage.taux
        if(imposable*taux>3600001):
            ipr=((4860.0+ 245699.85 +539999.70)+(((imposable*taux)-3600001)*reglage.taux_pallier4))           
        elif (imposable*taux>1800001):
            ipr= ((4860.0+245699.85)+((imposable*taux)-1800001)*reglage.taux_pallier3)
        elif((imposable*taux)>162001):
            ipr= 4860.0+(((imposable*taux)-162001.00)*reglage.taux_pallier2)
        elif(imposable*taux<162001):
            ipr= imposable*taux*reglage.taux_pallier1               
        return ipr
        
    @api.multi
    def compute_sheet(self):
        for payslip in self:
            
            if payslip.annee and payslip.mois:
                if payslip.employee_id:
                    
                    for heures in payslip.employee_id.heurs_prestations:
                        if heures.moi==payslip.mois:
                            
                            payslip.heures_prestation=heures
                            logging.info("================================heures du jours========================")
                            logging.info(heures.nombre_jours)
                            logging.info(heures.heure_sup_R2)
                            logging.info(heures.heure_sup_R1)
                            logging.info(heures.heure_sup_R3)
                            payslip.nombre_jours=heures.nombre_jours
                            payslip.heure_sup_R1=heures.heure_sup_R1
                            payslip.heure_sup_R2=heures.heure_sup_R2
                            payslip.heure_sup_R3=heures.heure_sup_R3
                            payslip.heure_sup_Nuit=heures.heure_sup_Nuit
                            payslip.autres_paiements=heures.autres_paiements
        
        return super(HrPayslip, self).compute_sheet()
        
    @api.depends('line_ids')
    def _compute_paiement_values(self):
        for payslip in self:
            for line in payslip.line_ids:
                if line.code:
                    if line.code =="NET":
                        payslip.salaire_net=line.total 
                    elif line.code =="BASIC":
                        payslip.salaire_base=line.total
                    elif line.code =="GROSS":
                        payslip.salaire_brut=line.total
                    elif line.code =="CNSS":
                        payslip.cnss=line.total
                    elif line.code =="TRANS":
                        payslip.transport=line.total
                    elif line.code =="LOG":
                        payslip.logement=line.total
                    elif line.code =="IMPOSABLES":
                        payslip.imposable = line.total
                    elif line.code == "IPR":
                        payslip.ipr=line.total
            
    
class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    mois=fields.Selection([(1,"Janvier"),(2,"Fevrier"),(3,"Mars"),(4,"Avril"),(5,"Mai"),(6,"Juin"),(7,"Juillet"),(8,"Aout"),(9,"Septembre"),(10,"Octobre"),(11,"Novembre"),(10,"Decembre")],string="Moi conserne", required="True")
    annee=fields.Selection([(y, str(y)) for y in range(1970, (datetime.now().year + 30)+1 )],string="Année: ex. '2020'",required="True")

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet_2(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note','mois','annee'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        mois = run_data.get('mois')
        annee = run_data.get('annee')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': employee.contract_id.id,
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
                'mois':mois,
                'annee': annee,
                
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}    
class HrExpense(models.Model):

    _inherit = "hr.expense"
    
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'Submitted'),
        ('approved', 'Approved'),
        ('approved1', 'Approved by Finance'),
        ('dg_approved', 'Approved by DG'),
        ('approved2', 'Approved by Gceo'),
        ('done', 'Paid'),
        ('refused', 'Refused')
    ], compute='_compute_state', string='Status', copy=False, index=True, readonly=True, store=True, help="Status of the expense.")
    department_id = fields.Many2one(
        string='Departement',comodel_name='hr.department',
        related='employee_id.department_id', depends=['employee_id'], store=True, ondelete='restrict',
    )
    
    
    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        
        compute=super(HrExpense, self)._compute_state()
        for expense in self:

            if expense.sheet_id.state == "approve2":
                expense.state = "approved2"
                
            if expense.sheet_id.state == "dg_approve":
                expense.state = "dg_approved"
            
    
        return compute
    
class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('approve1', 'Approved by Finance'),
        ('dg_approve', 'Approved by DG'),
        ('approve2', 'Approved by Gceo'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused')
    ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='draft', required=True, help='Expense Report State')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    
    @api.model
    def notification_standard(self,messages,employee,email,objet,to,cc):
        # import smtplib     
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")
        receivers_email = employee.work_email           
        agent=employee.name
        
        message= MIMEMultipart('alternative')
        message['To'] = to
        message['CC'] = cc
        message['Subject'] = objet
        
        message_texte = messages
        mt_html = MIMEText(message_texte, "html")
        message.attach(mt_html)
        server.sendmail("notification@bensizwe.com", email, message.as_string())
        server.quit()
        
    @api.multi
    def refuse_sheet(self, reason):
        
        logging.info("============reason===========")
        logging.info(reason)
        for sheet in self:
            employee=sheet.employee_id
            email=employee.work_email
            messages="Hi "+employee.name+" !<br> your requisition has been Refused for this reason:"+str(reason)
            objet="NOTIFICATION REQUISITION REFUSED"
            to=email
            cc="daddy@bensizwe.com"
            sheet.notification_standard(messages,employee,email,objet,to,cc)
        super(HrExpenseSheet, self).refuse_sheet(reason)
               
    @api.model
    def notification_expense(self):
        #    import smtplib       
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")
        
        for expense in self:
            
            if expense :
                receivers_email1 = "arnold.bukasa1@gmail.com"
                #receivers_email3 = "arnold.bukasa1@gmail.com"
                finance_notifs= self.env["res.users"].search([("estfinadmin","=",True)])
                gceo_notifis= self.env["res.users"].search([("estgceoadmin","=",True)])
                logging.info("======================== finance users =============================")
                logging.info(finance_notifs)
                logging.info(gceo_notifis)
                
                logging.info("======================== Etat  =============================")
                logging.info(self.state)
                
                if expense.employee_id:
                    receivers_email2 = expense.employee_id.work_email           
                    agent=expense.employee_id.name
                    message= MIMEMultipart('alternative')
                    message['To'] = "daddy@bensizwe.com"
                    message['CC'] = "daddy@bensizwe.com"
                    message['Subject'] = "Notification expenses"
                    
                    if self.state=="submit":
                        message_texte = str("Hi "+agent+"!<br> your requisition has been submitted to your Manager")
                    elif self.state=="approve":
                        message_texte = str("Hi "+agent+"!<br>your requisition has been validated by the Manager, and is now being processed at Finance")
                    elif self.state=="approve1":
                        message_texte = str("Hi "+agent+"!<br>, your request is sent to Gceo ")
                    elif self.state=="approve2":
                        message_texte = str("Hi"+agent+"!<br>the Gceo has validated your request ")
                    elif self.state=="dg_approve":
                        message_texte = str("Hi "+agent+"!<br>the MD has validated your request, and is now being processed to GCEO ")
                        
                    
                    mt_html = MIMEText(message_texte, "html")
                    message.attach(mt_html)
                    #server.sendmail("notification@bensizwe.com", receivers_email1, message.as_string())
                    
                    if receivers_email2:
                        server.sendmail("notification@bensizwe.com", receivers_email2, message.as_string())
                        #server.sendmail("itsupport@bensizwe.com", receivers_email3, message)
                    if self.state=="submit":
                        if expense.employee_id.department_id.manager_id:
                            
                            logging.info("======================== manager de l agent  =============================")
                            logging.info(expense.employee_id.department_id.manager_id.name)
                            
                            manager=expense.employee_id.department_id.manager_id
                            new_message_texte = str("Hi! "+manager.name+"!<br> there is requisition  submitted by "+agent+", please login in this link http://apps.bensizwe.com/web/login to confirm")
                            
                            if manager.work_email:
                            
                                new_message= MIMEMultipart('alternative')
                                new_message['To'] = manager.work_email
                                new_message['CC'] = "daddy@bensizwe.com"
                                new_message['Subject'] = "Notification expenses"
                                
                                logging.info("======================== adresse email du manager =============================")
                                logging.info(manager.work_email)
                                logging.info("======================== message du manager =============================")
                                logging.info(new_message)
                                
                                mt_html = MIMEText(new_message_texte, "html")
                                new_message.attach(mt_html)
                                logging.info("======================== message du manager apres affectation=============================")
                                logging.info(new_message)
                                server.sendmail("notification@bensizwe.com", manager.work_email, new_message.as_string())
                    
                    if self.state=="approve":
                        for department in self.env["hr.department"].search([("name","=","FINANCE")],limit=1):
                            manager_finance=department.manager_id
                            
                            logging.info("======================== nom du manager finance =============================")
                            logging.info(manager_finance.name)
                                                        
                            
                            finance_message_texte = str("Hi! "+manager_finance.name+"!<br>There is a requisition from "+agent+", and approved by is line, please login in this link http://apps.bensizwe.com/web/login to process")
                            
                            if manager_finance.work_email:
                                finance_message= MIMEMultipart('alternative')
                                finance_message['To'] = manager_finance.work_email
                                finance_message['CC'] = "daddy@bensizwe.com"
                                finance_message['Subject'] = "Notification expenses"
                                
                                logging.info("======================== adresse email manager  =============================")
                                logging.info(manager_finance.work_email)
                                
                                mt_html = MIMEText(finance_message_texte, "html")
                                
                                finance_message.attach(mt_html)
                                server.sendmail("notification@bensizwe.com", manager_finance.work_email, finance_message.as_string())

                    if self.state=="approve2":
                        for department in self.env["hr.department"].search([("name","=","FINANCE")],limit=1):
                            manager_finance=department.manager_id
                            
                            logging.info("======================== nom du manager finance =============================")
                            logging.info(manager_finance.name)

                            finance_message_texte = str("Hi! "+manager_finance.name+"!<br>the Gceo has validated the request from "+agent+", please login in this link http://apps.bensizwe.com/web/login to process")
                            
                            if manager_finance.work_email:
                                finance_message= MIMEMultipart('alternative')
                                finance_message['To'] = manager_finance.work_email
                                finance_message['CC'] = "daddy@bensizwe.com"
                                finance_message['Subject'] = "Notification expenses"
                                
                                logging.info("======================== adresse email manager  =============================")
                                logging.info(manager_finance.work_email)
                                
                                mt_html = MIMEText(finance_message_texte, "html")
                                
                                finance_message.attach(mt_html)
                                server.sendmail("notification@bensizwe.com", manager_finance.work_email, finance_message.as_string())
                        
                        #=================== notification tout le finance===================
                        for finance_notif in finance_notifs:
                            if finance_notif.employee_ids:
                                for employee in finance_notif.employee_ids:
                                    if employee.work_email:
                                        tout_finance_message= MIMEMultipart('alternative')
                                        tout_finance_message['To'] = employee.work_email
                                        tout_finance_message['CC'] = "daddy@bensizwe.com"
                                        tout_finance_message['Subject'] = "Notification expenses"
                                        mail=employee.work_email
                                        logging.info("======================== mail de chaque employe finance =============================")
                                        logging.info(mail)
                                
                                        message_texte = str("Hi! "+employee.name+"!<br>the Gceo has validated the request from "+agent)
                                        mt_html = MIMEText(message_texte, "html")
                                        tout_finance_message.attach(mt_html)
                                        server.sendmail("notification@bensizwe.com",mail, tout_finance_message.as_string())
                                
                                        
                    if self.state=="approve1":
                        users= self.env["res.users"].sudo().search([("name","!=","")])
                        logging.info("======================== Users dans finance approve =============================")
                        logging.info(users)
                        for user in users:
                            if user.estdg:
                                dgs= self.env["hr.employee"].sudo().search([("user_id","=",user.id)])
                                logging.info("======================== Users avec droit DG =============================")
                                logging.info(dgs)                               
                                #dg=user
                                for dg in dgs:
                                    if dg :
                                    #for department in self.env["hr.department"].search([("name","=","GCEO'S OFFICE")],limit=1):
                                        #manager_gceo=department.manager_id
                                        
                                        if dg:
                                            logging.info("======================== nom du DG =============================")
                                            logging.info(dg.name)
                                            
                                            dg_message_texte = str("Hi! "+dg.name+"!<br>the Finance has approved the request over 2500$ from  "+agent+" please login in this link http://apps.bensizwe.com/web/login to confirm")
                                            
                                            if dg.work_email:
                                                dg_message= MIMEMultipart('alternative')
                                                dg_message['To'] = dg.work_email
                                                dg_message['CC'] = "daddy@bensizwe.com"
                                                dg_message['Subject'] = "Notification expenses"
                                                logging.info("======================== adresse email du DG  =============================")
                                                logging.info(dg.work_email)
                                                
                                                mt_html = MIMEText(dg_message_texte, "html")
                                                dg_message.attach(mt_html)
                                                server.sendmail("notification@bensizwe.com", dg.work_email, dg_message.as_string())
                    if self.state=="dg_approve":
                         #=================== notification tout le Gceo===================
                        for gceo_notif in gceo_notifis:
                            if gceo_notif.employee_ids:
                                for employee in gceo_notif.employee_ids:
                                    if employee.work_email:
                                        mail=employee.work_email
                                        logging.info("======================== mail de l employe Gceo=============================")
                                        logging.info(mail)
                                        
                                        tout_gceo_message= MIMEMultipart('alternative')
                                        tout_gceo_message['To'] = mail
                                        tout_gceo_message['CC'] = "daddy@bensizwe.com"
                                        tout_gceo_message['Subject'] = "Notification expenses: GCEO Approval required!"
                                        
                                        tout_gceo_message_texte = str("Hi! "+employee.name+"!<br>there is an expense submitted by"+agent+", approved by the MD, and awaiting your approval")
                                        mt_html1 = MIMEText(tout_gceo_message_texte, "html")
                                        
                                        
                                        tout_gceo_message.attach(mt_html1)
                                        server.sendmail("notification@bensizwe.com",mail, tout_gceo_message.as_string())
                                        logging.info("======================== le message pour  Gceo=============================")
                                        logging.info(tout_gceo_message.as_string())
                                                  
                    #=========================notification finace  au moment de l'approbation==============                   
                    if self.state=="approve":
                        #=================== notification tout le finance===================
                        for finance_notif in finance_notifs:
                            if finance_notif.employee_ids:
                                for employee in finance_notif.employee_ids:
                                    if employee.work_email:
                                        mail=employee.work_email
                                        logging.info("======================== mail de l employe finance =============================")
                                        logging.info(mail)
                                        
                                        message= MIMEMultipart('alternative')
                                        message['To'] = mail
                                        message['CC'] = "daddy@bensizwe.com"
                                        message['Subject'] = "Notification expenses"
                                        mt_html = MIMEText(message_texte, "html")
                                        message_texte = str("Hi! "+employee.name+"!<br>there is  validated requisition from "+agent+", and approved by is line, please login in this link http://apps.bensizwe.com/web/login to process")
                                        mt_html = MIMEText(message_texte, "html")
                                        message.attach(mt_html)
                                        server.sendmail("notification@bensizwe.com",mail, message.as_string())                
        server.quit()
    
    @api.multi
    def write(self, vals):
        if "state" in vals:
            if vals['state'] == 'approve':
                
                if  ( self.env.uid != self.employee_id.department_id.manager_id.user_id.id ):
                    
                    if ( self.env.uid != self.employee_id.expense_manager_id.user_id.id):
                        respons=""
                        if self.employee_id.expense_manager_id:
                            respons=self.employee_id.expense_manager_id.name
                        logging.info("=====expense resposibles=========")
                        logging.info(self.employee_id.department_id.manager_id.user_id.name)
                        logging.info(self.employee_id.expense_manager_id.user_id.name)   
                        raise UserError(_("You are not a hexpense responsible for "+self.employee_id.name+" is expense responsible is "+respons))
                
                server = smtplib.SMTP('smtp.office365.com', 587)
                server.starttls()
                server.login("notification@bensizwe.com", "Fug42481")
                
                
                for expense in self:
                    
                    if expense :
                        
                                       
                        if expense.employee_id:
                            receivers_email2 = expense.employee_id.work_email           
                            agent=expense.employee_id.name
                            message= MIMEMultipart('alternative')
                            message['To'] = "daddy@bensizwe.com"
                            message['CC'] = "daddy@bensizwe.com"
                            message['Subject'] = "Notification expenses"
                           
                            
                            for department in self.env["hr.department"].search([("name","=","FINANCE")],limit=1):
                                manager_finance=department.manager_id
                                
                                logging.info("======================== nom du manager finance =============================")
                                logging.info(manager_finance.name)
                                
                                message_texte = str("Hi! "+manager_finance.name+"!<br>there is a validated requisition from  "+agent+", and approved by is line, please login in this link http://apps.bensizwe.com/web/login to process")
                                
                                if manager_finance.work_email:
                                    
                                    logging.info("======================== adresse email manager  =============================")
                                    logging.info(manager_finance.work_email)
                                    
                                    mt_html = MIMEText(message_texte, "html")
                                    message.attach(mt_html)
                                    server.sendmail("notification@bensizwe.com", manager_finance.work_email, message.as_string())
                            
                server.quit()
            
            if vals['state'] == 'submit':
                logging.info("================== environnement user================")
                logging.info(self.env.uid)
                logging.info("================== emploeyee user================")
                logging.info(self.employee_id.user_id.id)
                
                if  ( self.env.uid != self.employee_id.user_id.id):
                    raise UserError(_("You can sumbit only your hown requisition"))
            
                    
        res = super(HrExpenseSheet, self).write(vals)
        
    
    @api.multi
    def approvedg_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_user'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id | self.employee_id.expense_manager_id

            if self.employee_id.user_id == self.env.user :
                if self.employee.department_id:
                    if self.employee.department_id.manager_id.user_id != self.employee_id.user_id: 
                        raise UserError(_("You cannot approve your own expenses"))

            if not self.env.user in current_managers:
                raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        if self.total_amount <= 5000:
            self.write({'state': 'approve2', 'user_id': responsible_id})
            self.notification_expense()
            self.activity_update()
        else :
            self.write({'state': 'dg_approve', 'user_id': responsible_id})
            self.notification_expense()
            self.activity_update()
            
    
    @api.multi
    def approvegceo_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_user'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id | self.employee_id.expense_manager_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

            if not self.env.user in current_managers:
                raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({'state': 'approve2', 'user_id': responsible_id})
        self.notification_expense()
        self.activity_update()
        
    @api.multi
    def approvefinacy_expense_sheets(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_user'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id | self.employee_id.expense_manager_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

            if not self.env.user in current_managers:
                raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        if self.total_amount <= 2500:
            
            self.write({'state': 'approve2', 'user_id': responsible_id})
            self.notification_expense()
            self.activity_update()
        else :
            self.write({'state': 'approve1', 'user_id': responsible_id})
            self.notification_expense()
            self.activity_update()







class Users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    _description = 'Utilisateurs'
    
    estfinadmin = fields.Boolean("Est admin Finance?")
    estgceoadmin = fields.Boolean("Est admin Gceo?")
    estdg = fields.Boolean("Est DG?")
    
    @api.multi
    def write(self, vals):
        """ Synchronize user and its related employee """
        
                
        logging.info("===================== Valeurs de users modifie ================")
        logging.info(vals)
        
        finacegroup=self.env["res.groups"].search([("name","=","Finance Manager")],limit=1).id
        gceogroup=self.env["res.groups"].search([("name","=","GCEO Manager")],limit=1).id
        dggroup=self.env["res.groups"].search([("name","=","DG")],limit=1).id
        
        idf=str(finacegroup)
        idg=str(gceogroup)
        idd=str(dggroup)
        
        financegroup_id=str("in_group_"+idf)
        gceogroup_id=str("in_group_"+idg)
        dggroup_id=str("in_group_"+idd)
        
        logging.info("===================== goupes consernés ================")
        logging.info(financegroup_id)
        logging.info(gceogroup_id)
        logging.info(dggroup_id)
              

        if financegroup_id in vals:
            if vals[financegroup_id] == True:
                vals["estfinadmin"]= True
                
                logging.info("===================== est il admin finance ================")
                
                logging.info(vals["estfinadmin"])
                
        if gceogroup_id in vals:
            if vals[gceogroup_id] == True:
                vals["estgceoadmin"]= True
                logging.info("===================== est il admin Gceo ================")
                
                logging.info(vals["estgceoadmin"])
                
        if dggroup_id in vals:
            if vals[dggroup_id] == True:
                vals["estdg"]= True
                logging.info("===================== est il DG ================")
                
                logging.info(vals["estdg"])
                
        #if employee_values:
        #    self.env['hr.employee'].sudo().search([('user_id', 'in', self.ids)]).write(employee_values)
        result = super(Users, self).write(vals)
        return result
    
    
    @api.one
    @api.onchange("groups_id")
    def _onchange_groups_id(self):
        
        finace_group=self.env["res.groups"].search([("name","=","Finance Manager")])
        gceo_group=self.env["res.groups"].search([("name","=","Gceo Manager")])
        
        logging.info("===================== finance groupe ================")
        logging.info(finace_group)
               
        logging.info("===================== user groupes ================")
        logging.info(self.groups_id)
        logging.info("===================== user groupes ================")
        logging.info(self.id)
        logging.info("===================== user groupes ================")
        logging.info(self.login)
        logging.info("===================== self ================")
        logging.info(self)
     
        
        if finace_group in self.groups_id  :
            self.estfinadmin = True
            logging.info("===================== verif adminfinace ================")
            logging.info(self.estfinadmin)
        else :
            self.estfinadmin = False
            logging.info("===================== verif adminfinace ================")
            logging.info(self.estfinadmin)
        
class ResPartner(models.Model):
    _inherit = 'res.partner'
    membres= fields.Integer(string="Familly informations")
    achats = fields.One2many('achats','client_id', string="Achats et approvisionnements")
    
class Achats(models.Model):
    _name = "achats"
    
    produit = fields.Char(string="Produit")
    quantite= fields.Char(string="Quantité")
    date_achat= fields.Date(string="Date Achat | Recharge")
    client_id = fields.Many2one('res.partner', string='Costumer' )