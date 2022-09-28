
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class EmployeAttendanceWizard(models.TransientModel):
    _name = "hr.attendance.employee.report"
    _description = 'Employee attendance'

    month_list = [('01','January'),('02','February'),('03','March'),('04','April'),('05','May'),
                  ('06','June'),('07','July'),('08','August'),('09','September'),('10','October'),
                  ('11','November'),('12','December')]
    month = fields.Selection(month_list,string='Month', required=True)
    year = fields.Selection([('2015','2015'),('2016','2016'),('2017','2017'),
                             ('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),
                             ('2022','2022'),('2023','2023'),('2024','2024')
                                ,('2025','2025'),('2026','2026'),('2027','2027')],string='Year',required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employee")
    date_from = fields.Date('Date from',)
    date_to = fields.Date('Date to', )

    # Print Report Action
    def action_print(self):
        self.ensure_one()
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        if self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
            if not self.employee_ids:
                raise ValidationError(_("Enter value in employee field."))
        if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
            if not self.employee_ids:
                self.employee_ids = [(6, 0, employee.ids)]
        day = '/31/' if self.month in ['01','03','05','07','08','10','12'] else '/30/'
        date_from = datetime.strptime(self.month + '/01/' + self.year, '%m/%d/%Y').date()
        date_to = datetime.strptime(self.month + day + self.year, '%m/%d/%Y').date()
        [data] = self.read()
        datas = {
            'model': 'hr.attendance',
            'employee_ids': self.employee_ids.ids,
            'date_from': date_from,
            'date_to': date_to,
            'month': self.month,
            'year': self.year,
        }
        if data['employee_ids']:
            datas['employee_ids'] = self.employee_ids.ids
        if not data['employee_ids']:
            if not employee:
                raise ValidationError(_("No employee against current logged in user."))
            datas['employee_ids'] = employee.ids
        return self.env.ref('eyk_attendance_modification.attendance_report_for_employees').report_action(self, data=datas)

    # Print Report Action
    def _print_report(self,data):
        return self.env.ref('eyk_attendance_modification.attendance_report_for_employees').report_action(self, data=data, config=False)


