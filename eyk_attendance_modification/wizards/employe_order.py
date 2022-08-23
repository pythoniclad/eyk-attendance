
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
import time 
import base64 
import calendar 
from odoo.tests.common import Form

class EmployeOrder(models.TransientModel):
    _name="employe.order"
    _description='Employe Order'

    month_list = [('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]
    month = fields.Selection(month_list,string='Month',required=True)
    year = fields.Selection([('2015','2015'),('2016','2016'),('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022'),('2023','2023'),('2024','2024'),('2025','2025'),('2026','2026')],string='Year')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')

    # Print Report Action
    def action_print(self):
        data = {}
        data['Employe_Order'] = self.env.context.get('active_id')
        action=  self.env.ref('eyk_attendance_modification.maintenance_request_report')\
            .with_context(discard_logo_check=True).report_action(self)
        action.update({'close_on_report_download':True})
        return action

    # Print Report Action
    def _print_report(self,data):
        return self.env.ref('eyk_attendance_modification.maintenance_request_report').report_action(self, data=data, config=False)


