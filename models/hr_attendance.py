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

        # Prepare the email content
        attendance_summary = """
        <html>
        <body>
            <h2>Résumé des présences pour la journée :</h2>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <thead>
                    <tr>
                        <th>Employé</th>
                        <th>Check-in</th>
                        <th>Check-out</th>
                    </tr>
                </thead>
                <tbody>
        """
        for attendance in attendances:
            attendance_summary += f"""
                    <tr>
                        <td>{attendance.employee_id.name}</td>
                        <td>{attendance.check_in}</td>
                        <td>{attendance.check_out}</td>
                    </tr>
            """
        attendance_summary += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Send the email
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login("notification@bensizwe.com", "Fug42481")

        receivers_email = "arnold.bukasa1@gmail.com"
        message = MIMEMultipart('alternative')
        message['To'] = receivers_email
        message['CC'] = "recrutement@bensizwe.com"
        message['Subject'] = "Résumé des présences et feuilles de temps"

        mt_text = MIMEText(attendance_summary, "html")
        message.attach(mt_text)
        server.sendmail("notification@bensizwe.com", receivers_email, message.as_string())

        server.quit()

        logging.info("Daily attendance notification sent successfully.")