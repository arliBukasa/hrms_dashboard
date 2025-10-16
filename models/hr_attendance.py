# -*- coding: utf-8 -*-
import logging
import logging
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def notify_daily_attendance(self):
        # Get today's date
        today = fields.Date.today()

        # Collect attendance data
        attendances = self.env['hr.attendance'].search([('check_in', '>=', today)])

        # Get all active employees
        active_employees = self.env['hr.employee'].search([('active', '=', True)])
        
        # Get list of employees who checked in today
        present_employee_ids = [att.employee_id.id for att in attendances]
        
        # Calculate absent employees
        absent_employees = active_employees.filtered(lambda emp: emp.id not in present_employee_ids)
        
        # Calculate absenteeism rate
        total_employees = len(active_employees)
        total_absent = len(absent_employees)
        total_present = len(present_employee_ids)
        absenteeism_rate = (total_absent / total_employees * 100) if total_employees > 0 else 0

        # Group attendances by department
        attendances_by_dept = {}
        for attendance in attendances:
            dept_name = attendance.employee_id.department_id.name if attendance.employee_id.department_id else "Sans département"
            if dept_name not in attendances_by_dept:
                attendances_by_dept[dept_name] = []
            attendances_by_dept[dept_name].append(attendance)

        # Prepare the email content with inline styles for better email client compatibility
        attendance_summary = """
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px;">
            <h2 style="color: #333;">Résumé des présences pour la journée</h2>
            
            <!-- SYNTHÈSE -->
            <div style="background-color: #FFC000; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0; color: #333;">SYNTHÈSE</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px; background-color: white;">
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f0f0f0; width: 60%;">Total employés actifs</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{total_employees}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f0f0f0;">Employés présents</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{total_present}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f0f0f0;">Employés absents</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{total_absent}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; background-color: #f0f0f0;">Taux d'absentéisme</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{absenteeism_rate:.2f}%</td>
                    </tr>
                </table>
            </div>
        """.format(
            total_employees=total_employees,
            total_present=total_present,
            total_absent=total_absent,
            absenteeism_rate=absenteeism_rate
        )

        logging.info(f"Total employés: {total_employees}, Présents: {total_present}, Absents: {total_absent}")
        logging.info(f"Départements trouvés: {list(attendances_by_dept.keys())}")
        logging.info(attendance_summary)

        # Add absent employees section
        if absent_employees:
            attendance_summary += """
            <div style="background-color: #FF6B6B; color: white; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0;">LISTE DES AGENTS ABSENTS</h3>
            </div>
            <table style="width: 100%; border-collapse: collapse; background-color: white; color: black; margin-bottom: 20px;">
                <thead>
                    <tr>
                        <th style="background-color: #f0f0f0; padding: 10px; border: 1px solid #ddd; text-align: left;">Nom de l'employé</th>
                        <th style="background-color: #f0f0f0; padding: 10px; border: 1px solid #ddd; text-align: left;">Département</th>
                    </tr>
                </thead>
                <tbody>
            """
            for emp in absent_employees:
                dept_name = emp.department_id.name if emp.department_id else "Sans département"
                attendance_summary += f"""
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">{emp.name}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{dept_name}</td>
                    </tr>
                """
            attendance_summary += """
                </tbody>
            </table>
            """

        # Add presence section grouped by department
        attendance_summary += """
            <div style="background-color: #92D050; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0; color: #333;">PRÉSENCES PAR DÉPARTEMENT</h3>
            </div>
        """

        # Sort departments alphabetically
        sorted_departments = sorted(attendances_by_dept.keys())
        
        for dept_name in sorted_departments:
            attendance_summary += f"""
            <div style="background-color: #B4C7E7; padding: 10px; margin: 15px 0 5px 0; font-weight: bold; font-size: 14px; border-radius: 3px;">{dept_name}</div>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
                <thead>
                    <tr>
                        <th style="background-color: #D7E4BC; padding: 10px; border: 1px solid #ddd; font-weight: bold; text-align: left;">Employé</th>
                        <th style="background-color: #D7E4BC; padding: 10px; border: 1px solid #ddd; font-weight: bold; text-align: left;">Check-in</th>
                        <th style="background-color: #D7E4BC; padding: 10px; border: 1px solid #ddd; font-weight: bold; text-align: left;">Check-out</th>
                    </tr>
                </thead>
                <tbody>
            """
            for attendance in attendances_by_dept[dept_name]:
                checkout = attendance.check_out if attendance.check_out else "En cours"
                attendance_summary += f"""
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">{attendance.employee_id.name}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{attendance.check_in}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{checkout}</td>
                    </tr>
                """
            attendance_summary += """
                </tbody>
            </table>
            """

        attendance_summary += """
        </body>
        </html>
        """
        logging.info(" ===================" + attendance_summary)
        # Send the email
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")

        receivers_email = "arnold.bukasa1@gmail.com"
        boss_email = "massif@bensizwe.com"
        message = MIMEMultipart('alternative')
        message['To'] = receivers_email
        message['CC'] = ""
        message['Subject'] = "Résumé des présences et feuilles de temps"

        mt_text = MIMEText(attendance_summary, "html")
        message.attach(mt_text)
        server.sendmail("notification@bensizwe.com", receivers_email, message.as_string())
        #server.sendmail("notification@bensizwe.com", boss_email, message.as_string())

        server.quit()

        logging.info("Daily attendance notification sent successfully.")