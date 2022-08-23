
{
    "name": "Attendance Modification",
    "version": "15.0.1.0.0",
    "depends": [
        "base", "hr", "hr_attendance"
    ],
    "data": [
        'security/ir.model.access.csv',
        'data/cron.xml',
        "views/views.xml",

        'wizards/employee_order_view.xml',
        'reports/employee_report_action.xml',
        'reports/employee_report_template.xml',
        'reports/single_manager_action.xml',
        'reports/single_manager_report_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'eyk_attendance_modification/static/src/js/scripts.js',
            'eyk_attendance_modification/static/src/css/style.css',
        ],
        'web.assets_qweb': [
            'eyk_attendance_modification/static/src/xml/*.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
