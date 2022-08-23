
import pytz
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time
from odoo import models, fields, api, exceptions, _
from odoo.tools import float_round
import base64
import datetime


class Employee(models.Model):
    _inherit = 'hr.employee'

    resource_monthly_limit = fields.Integer("Monthly Work Limit", default=0)
    hours_this_month = fields.Float(
        compute='_compute_hours_this_month', groups="hr_attendance.group_hr_attendance_user")
    hours_left_this_month = fields.Float(
        compute='_compute_hours_this_month', groups="hr_attendance.group_hr_attendance_user")
    hours_this_month_display = fields.Char(
        compute='_compute_hours_this_month', groups="hr_attendance.group_hr_attendance_user")

    def _compute_hours_this_month(self):
        now = fields.Datetime.now()
        now_utc = pytz.utc.localize(now)
        for employee in self:
            tz = pytz.timezone(employee.tz or 'UTC')
            now_tz = now_utc.astimezone(tz)
            start_tz = now_tz + relativedelta(months=0, day=1, hour=0, minute=0, second=0, microsecond=0)
            start_naive = start_tz.astimezone(pytz.utc).replace(tzinfo=None)
            end_tz = now_tz
            end_naive = end_tz.astimezone(pytz.utc).replace(tzinfo=None)

            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                '&',
                ('check_in', '<=', end_naive),
                ('check_out', '>=', start_naive),
            ])

            hours = 0
            for attendance in attendances:
                check_in = max(attendance.check_in, start_naive)
                check_out = min(attendance.check_out, end_naive)
                hours += (check_out - check_in).total_seconds() / 3600.0

            employee.hours_this_month = round(hours, 2)
            employee.hours_left_this_month = "%g" % round((employee.resource_monthly_limit - employee.hours_this_month),2)
            employee.hours_this_month_display = "%g" % employee.hours_this_month

    def _attendance_action(self, next_action):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
        action_message['previous_attendance_change_date'] = employee.last_attendance_id and (employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
        action_message['employee_name'] = employee.name
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        action_message['hours_today'] = employee.hours_today
        action_message['resource_monthly_limit'] = employee.resource_monthly_limit
        action_message['hours_left_this_month'] = employee.hours_left_this_month

        if employee.user_id:
            modified_attendance = employee.with_user(employee.user_id)._attendance_action_change()
        else:
            modified_attendance = employee._attendance_action_change()
        action_message['attendance'] = modified_attendance.read()[0]
        action_message['total_overtime'] = employee.total_overtime
        return {'action': action_message}

    total_day = fields.Char('day')
    total_hour = fields.Char('hour')
    present_day = fields.Char('present day')
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')

    # send mail functionality
    def send_employee_report(self):
        employee_ids = self.env['hr.employee'].search([])
        manager_ids = []
        for employee in employee_ids:
            if employee.parent_id and employee.parent_id not in manager_ids:
                manager_ids.append(employee.parent_id)
                for manager in manager_ids:
                    for res_user_id in self.env['res.users'].search([]):
                        partner_list = []
                        email_to = []
                        report_mail = {}
                        now = datetime.now()
                        year = now.year
                        month = now.month
                        month_date = date(int(now.year), int(now.month), 1)
                        date_from = month_date.replace(day=1)
                        today_date = date.today()
                        if today_date == date_from:
                            if res_user_id.has_group('hr.group_hr_manager'):
                                partner_list.append(res_user_id.partner_id.id)
                                content = "Please Find Attachment"
                                report_mail = {
                                    'subject': "Employee Attandance Report",
                                    'email_to': manager.name,
                                    'author_id': res_user_id.partner_id.id,
                                    'body_html': content,
                                }
                                name = "my attachment"
                                pdf = self.env.ref('eyk_attendance_modification.single_manager').render_qweb_pdf(
                                    manager.id)
                                b64_pdf = base64.b64encode(pdf[0])
                                attachment = self.env['ir.attachment'].create({
                                    'name': 'Attendance report for the ' + manager.name,
                                    'type': 'binary',
                                    'datas': b64_pdf,
                                    'res_model': self._name,
                                    'res_id': self.id,
                                    'mimetype': 'application/x-pdf'
                                })

                                if report_mail:
                                    mail_id = res_user_id.env['mail.mail'].sudo().create(report_mail)
                                    if mail_id:
                                        mail_id.send(res_user_id.id)
                                        mail_id.attachment_ids = [(6, 0, [attachment.id])]


from datetime import date
from datetime import timedelta


class Attendance(models.Model):
    _inherit = "hr.attendance"

    is_entry_splitted = fields.Boolean('Is Split?', default=False)

    def split_entries(self):
        prev_day = datetime.datetime.today() - datetime.timedelta(days=1)
        print('prev-day: ',prev_day)
        current = date.today() - timedelta(days = 0)
        prev = date.today() - timedelta(days = 1)
        attendances = self.env['hr.attendance'].sudo().search([('check_in', '>=', prev),
                                                               ('check_out', '>=', prev),
                                                               ('check_out', '<', current),
                                                               ('check_in', '!=', False),
                                                               ('check_out', '!=', False),
                                                               ('is_entry_splitted', '=', False)])

        hours = 0
        for attendance in attendances:
            print('worked_hours: ',attendance.worked_hours)
            check_out = attendance.check_out
            if attendance.worked_hours > 6.5:
                new_check_out = attendance.check_in + timedelta(hours=6)
                print(attendance.check_in)
                attendance.sudo().write({
                    'check_out': new_check_out,
                    'is_entry_splitted': True,
                })
                if new_check_out and check_out:
                    new_check_in = new_check_out + timedelta(minutes=30)
                    delta = new_check_out - check_out
                    new_worked_hours = delta.total_seconds() / 3600.0
                    self.env['hr.attendance'].sudo().create({
                        'employee_id': attendance.employee_id.id,
                        'check_in': new_check_in,
                        'check_out': check_out,
                        'is_entry_splitted': True,
                    })


