# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Aswani PC (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': "Odoo 12 Hrsm Dashboard",
    'version': '12.0.1.0.0',
    'summary': """for besizwe dashboard""",
    'description': """Open HRMS - HR Dashboard""",
    'category': 'Human Resources',
    'author': 'Arnold bukasa',
    'company': 'Arnold bukasa',
    'maintainer': 'Arbnold bukasa',
    'website': "https://www.bulkasoft.com",
    'depends': ['hr', 'hr_holidays', 'hr_timesheet', 'hr_payroll', 'hr_attendance', 'hr_timesheet_attendance',
                'hr_recruitment', 'hr_resignation', 'event', 'hr_reward_warning','hr_employee_updation'],
    'external_dependencies': {
        'python': ['pandas'],
    },
    "data": [
        "security/hrms_dashboard_security.xml",
        "security/ir.model.access.csv",
        "report/broadfactor.xml",
        "report/Report_cv.xml",
        "views/dashboard_views.xml",
        "views/hr_casual.xml",
        "views/hr_leave.xml",
        "views/hr_recruitement.xml",
        "views/contract_partner.xml",
        "views/mail_activity.xml",
        "views/hr_candidat.xml",
        "data/hr_attendance_cron.xml"
    ],
    'qweb': ["static/src/xml/hrms_dashboard.xml"],
    'images': ["static/description/banner.gif"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}