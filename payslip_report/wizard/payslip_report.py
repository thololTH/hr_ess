# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta



class PaySlipReport(models.Model):
    _name = 'pay.slip.report'

    employee = fields.Many2one('hr.employee', string='Employee')
    basic = fields.Char(string='Basic')
    allowance = fields.Char(string='Allowance')
    gross = fields.Char(string='Gross')
    deduction = fields.Char(string='Deduction')
    net = fields.Char(string='Net')
    

class PayslipReportWizard(models.TransientModel):
    _name = "pay.slip.report.wizard"
    
    def start_date(self):
        return datetime.strptime(str(datetime.today().date()), DEFAULT_SERVER_DATE_FORMAT) + \
                               relativedelta(months=0, day=1)

    date_from = fields.Date(string='Start Date',default=start_date)
    date_to = fields.Date(string='End Date', compute='compute_end_date')
    
    

    @api.depends('date_from')
    def compute_end_date(self):
        for rec in self:
            rec.date_to = datetime.strptime(str(rec.date_from), DEFAULT_SERVER_DATE_FORMAT) + \
                               relativedelta(months=1, day=1, days=-1)
 
    def get_data(self):
        domain = [('date_from', '>=', self.date_from ),('date_to', '<=', self.date_to )]
        payslip_report_obj = self.env['pay.slip.report']

        basic = allowance = gross = deduction = net = 0
        

        form_name = 'PaySlip Repord from ' + str(self.date_from) + ' to ' + str(self.date_to)
        payslip_obj = self.env['hr.payslip'].search(domain)
        payslip_rule_cate_obj = self.env['hr.salary.rule.category'].search([])


        for x in payslip_report_obj.search([]):
            x.unlink()


        if payslip_obj:
            for pay_obj in payslip_obj:
                print(pay_obj.line_ids)
                for lin in pay_obj.line_ids:
                    if lin.category_id.name == "Basic":
                        basic += lin.total
                    elif lin.category_id.name == 'Allowance':
                        allowance += lin.total
                    elif lin.category_id.name == 'Gross':
                        gross += lin.total
                    elif lin.category_id.name == 'Deduction':
                        deduction += lin.total
                    elif lin.category_id.name == 'Net':
                        net += lin.total
                
                
                payslip_report_obj.sudo().create({
                    'employee': pay_obj.employee_id.id,
                    'basic': basic,
                    'allowance': allowance,
                    'gross': gross,
                    'deduction': deduction,
                    'net': net,
                })
            
        
        return {
            'name':form_name,
            'type': 'ir.actions.act_window',
            'res_model': 'pay.slip.report',
            'view_mode': 'tree',
            'views': [(False, 'tree')],
            'target': 'current',
        }
