
import time
import datetime
import calendar
from odoo import api, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import date, datetime, time ,timedelta

class AttendanceReport(models.AbstractModel):
    _name = 'report.eyk_attendance_modification.emoloyee_report'
    _description = "Maintenance summary"

    #Get employee report value function
    def _get_report_values(self, docids, data=None):
        employee_ids = False
        manager_ids = False
        doc_model = False
        docs = False
        month = False
        self = self.env['hr.employee']
        if docids:
            active_id = docids
            docs = self.env['employe.order'].browse(docids)
            if docs:
                employee_ids = self.env['hr.employee'].search([])
                if employee_ids:
                    manager_ids = []
                    for employee in employee_ids:
                        total_hour = 0
                        month_date=date(int(docs.year),int(docs.month),1)
                        docs.date_from=month_date.replace(day=1)
                        docs.date_to=month_date.replace(day=calendar.monthrange(month_date.year,month_date.month)[1])
                        today = docs.date_from
                        wizard_month = int(docs.month)
                        day=date(int(docs.year), int(docs.month) ,1)
                        single_day = timedelta(days=1)
                        weekday = docs.month
                        days = 0
                        while day.month == today.month:
                            if day.isoweekday() == 5:
                                days += 1
                            day += single_day

                        today = docs.date_from
                        wizard_month = int(docs.month)
                        day=date(int(docs.year), int(docs.month) ,1)
                        single_day = timedelta(days=1)
                        weekday = docs.month
                        dayss = 0
                        while day.month == today.month:
                            if day.isoweekday() == 7:
                                dayss += 1
                            day += single_day 

                        week_day = dayss + days
                        monthday =  docs.date_to - docs.date_from 
                        monthday += timedelta(days=1)
                        total_day = (monthday.days) - week_day
                        total_hour = total_day * employee.resource_calendar_id.hours_per_day
                        employee.total_day = total_day
                        employee.total_hour = total_hour
                        employee.present_day = total_day
                        if employee.parent_id and employee.parent_id not in manager_ids :
                            manager_ids.append(employee.parent_id)
                            month = calendar.month_name[int(docs.month)]
                       
        return {
                   'manager_ids':manager_ids,
                   'employee_ids':employee_ids,
                   'doc_model':self.env['hr.employee'],
                   'docks': docs,
                   'month':month,
                   }
