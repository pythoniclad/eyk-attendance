
{
    "name": "Attendance Modifications",
    "version": "15.0.0.0",
    "depends": ["base", "hr", "hr_attendance"],
    "data": [
        'security/ir.model.access.csv',
        'data/cron.xml',
        "views/views.xml",
        
        'wizards/employee_attendance_wizard_view.xml',
        'reports/attendance_report.xml',
        'reports/report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eyk_attendance_modification/static/src/js/scripts.js',
        ],
        'web.assets_qweb': [
            'eyk_attendance_modification/static/src/xml/*.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
