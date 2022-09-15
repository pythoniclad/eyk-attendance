odoo.define('eyk_attendance_modification.attendance_greeting', function (require) {
"use strict";
var core = require('web.core');
var _t = core._t;
var greeting_message = require('hr_attendance.greeting_message');
greeting_message.include({
 	init: function(parent, action) {
        var self = this;
        this._super.apply(this, arguments);
        if(action.attendance) {
       		this.resource_monthly_limit = action.resource_monthly_limit
       		if (action.hours_left_this_month) {
            var duration = moment.duration(action.hours_left_this_month, "hours");
            this.hours_left_this_month = duration.hours() + _t(' hours, ') + duration.minutes() + _t(' minutes');
        }
       	}

    }
})
});