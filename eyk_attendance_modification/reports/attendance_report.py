
from datetime import timedelta, date

import dateutil.relativedelta
from dateutil.relativedelta import relativedelta

from odoo import models


class CustomReport(models.AbstractModel):
    _name = "report.eyk_attendance_modification.report_employee_attendance"
    _description = "Employee Attendance report"

    def _get_report_values(self, docids, data=None):
        print(data)
        attendances_data = []
        employees = self.env['hr.employee'].sudo().browse(data['employee_ids'])
        for employee in employees:
            attendances = self.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id)])
            doc = {
                'employee': employee.name,
                # 'attendances': attendances,
            }
            attendances_data.append(doc)
        print(attendances_data)
        return {
            'docs': attendances_data,
            'date_from': data['date_from'],
            'date_to': data['date_to'],
        }
