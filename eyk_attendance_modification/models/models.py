import pytz
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from odoo import models, fields, api, exceptions, _
from odoo.tools import float_round
from datetime import timedelta, date
import datetime


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    resource_monthly_limit = fields.Float(related='employee_id.resource_monthly_limit')
    has_reached_limit = fields.Boolean(related='employee_id.has_reached_limit')
    hours_this_month = fields.Float(related='employee_id.hours_this_month')
    hours_left_this_month = fields.Float(related='employee_id.hours_left_this_month')
    hours_this_month_display = fields.Char(related='employee_id.hours_this_month_display')

    total_day = fields.Char(related='employee_id.total_day')
    total_hour = fields.Char(related='employee_id.total_hour')
    present_day = fields.Char(related='employee_id.present_day')
    date_from = fields.Date(related='employee_id.date_from')
    date_to = fields.Date(related='employee_id.date_to')


class Employee(models.Model):
    _inherit = 'hr.employee'

    resource_monthly_limit = fields.Float("Monthly Work Limit", default=0.0)
    has_reached_limit = fields.Boolean("Has Reached Limit?")
    hours_this_month = fields.Float(
        compute='_compute_hours_this_month', groups="hr_attendance.group_hr_attendance_user")
    hours_left_this_month = fields.Float(
        compute='_compute_hours_this_month', groups="hr_attendance.group_hr_attendance_user")
    hours_this_month_display = fields.Char(
        compute='_compute_hours_this_month', groups="hr_attendance.group_hr_attendance_user")

    def reset_workhours_monthly(self):
        employees = self.env['hr.employee'].sudo().search([])
        for employee in employees:
            employee.sudo().write({
                    'hours_this_month': 0.00,
                    'hours_left_this_month': 0.00,
                    'hours_this_month_display': '',
                    'has_reached_limit': False,
                })

    def detect_workhours_limit(self):
        now = fields.Datetime.now()
        now_utc = pytz.utc.localize(now)
        employees = self.env['hr.employee'].sudo().search([('last_check_in', '!=', False), ('last_check_out', '=', False)])
        for employee in employees:
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False),
            ])
            diff = 0
            for attendance in attendances:
                delta = now - attendance.check_in
                diff = delta.total_seconds() / 3600.0
            if (employee.hours_left_this_month - diff) <= 0.1:
                tz = pytz.timezone(employee.tz or 'UTC')
                now_tz = now_utc.astimezone(tz)
                if not employee.last_attendance_id.check_out:
                    employee.last_attendance_id.check_out = datetime.datetime.now()
                employee.has_reached_limit = True
            else:
                employee.has_reached_limit = False

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
                check_in = attendance.check_in
                check_out = attendance.check_out
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


class Attendance(models.Model):
    _inherit = "hr.attendance"

    is_entry_splitted = fields.Boolean('Is Split?', default=False)
    type = fields.Selection([('break', 'Break'),('work', 'Work'),], string='Type')

    @api.model
    def create(self, vals):
        if 'employee_id' in vals:
            employee_id = self.env['hr.employee'].browse(vals.get("employee_id"))
            if employee_id:
                if employee_id.has_reached_limit:
                    if employee_id.name:
                        raise ValidationError(_(str(employee_id.name) + " have reached monthly limit\nContact admin!"))
                    else:
                        raise ValidationError(_("You have reached your monthly limit\nContact your admin!"))
        employee = super(Attendance, self).create(vals)
        return employee

    def split_entries(self):
        prev_day = datetime.datetime.today() - datetime.timedelta(days=1)
        current = date.today() - timedelta(days = 0)
        prev = date.today() - timedelta(days = 1)
        attendances = self.env['hr.attendance'].sudo().search([('check_in', '>=', prev),
                                                               ('check_out', '>=', prev),
                                                               ('check_out', '<=', current),
                                                               ('check_in', '!=', False),
                                                               ('check_out', '!=', False),
                                                               ('is_entry_splitted', '=', False)])

        hours = 0
        for attendance in attendances:
            check_out = attendance.check_out
            worked_hours = attendance.worked_hours
            if attendance.worked_hours > 6.0:
                new_check_out = attendance.check_in + timedelta(hours=6)
                attendance.sudo().write({
                    'check_out': new_check_out,
                    'is_entry_splitted': True,
                    'type': 'work',
                })
                if new_check_out and check_out and worked_hours > 6.5:
                    new_check_in = new_check_out + timedelta(minutes=30)
                    delta = new_check_out - check_out
                    new_worked_hours = delta.total_seconds() / 3600.0
                    self.env['hr.attendance'].sudo().create({
                        'employee_id': attendance.employee_id.id,
                        'check_in': new_check_in,
                        'check_out': check_out,
                        'is_entry_splitted': True,
                        'type': 'break',
                    })