# -*- coding: utf-8 -*-

from odoo import models, fields, api


class pettycash(models.Model):
    _name = 'pettycash.pettycash'
    _description = 'pettycash.pettycash'

    name = fields.Many2one('hr.employee', "Name", required=True)
    account = fields.Many2one('account.account', "Account")
    value2 = fields.Float("Amount")
    description = fields.Text("Reason")
    # date_of_issue = fields.Date("Date of Issue")
    date_of_request = fields.Date("Date of request",default=fields.Date.context_today)
    state = fields.Selection([ ('draft', 'Draft'),
        ('request', 'Request'),
        ('approve', 'Approve'),('cancel', 'Cancel')],default='draft')


    def action_request(self):
        self.state = 'request'


    def action_approve(self):
        self.state = 'approve'


    def action_cancel(self):
        self.state = 'cancel'

