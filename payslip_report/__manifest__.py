# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : "Payslip Report",
    'version' : '1.0',
    'summary': '',
    'sequence': 3,
    'description':'',
    'category': 'Custom',
    'website': '',
    'depends' : ['base', 'hr_payroll'],

    'data': [
            'wizard/payslip_report.xml',
            'security/ir.model.access.csv',
            
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

