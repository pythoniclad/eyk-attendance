
from datetime import timedelta, date
import calendar
import dateutil.relativedelta
from dateutil.relativedelta import relativedelta

from odoo import models


class CustomReport(models.AbstractModel):
    _name = "report.eyk_attendance_modification.report_employee_attendance"
    _description = "Employee Attendance report"

    def _get_report_values(self, docids, data=None):
        attendances = []
        emp_ids = []
        has_records = []
        employees = self.env['hr.employee'].sudo().browse(data['employee_ids'])
        for employee in employees:
            attendance_ids = self.env['hr.attendance'].sudo().search([('employee_id', '=', employee.id),
                                                                      ('check_in', '>=', data['date_from']),
                                                                      ('check_out', '<=', data['date_to'])])
            emp_ids.append(employee)
            attendances.append(attendance_ids)
            x = True if attendance_ids else False
            has_records.append(x)
        return {
            'docs': attendances,
            'employee_ids': emp_ids,
            'has_records': has_records,
            'month': calendar.month_name[int(data['month'])],
            'year': data['year'],
            'date_from': data['date_from'],
            'date_to': data['date_to'],
        }
