# -*- coding: utf-8 -*-
# from odoo import http


# class Pettycash(http.Controller):
#     @http.route('/pettycash/pettycash/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pettycash/pettycash/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pettycash.listing', {
#             'root': '/pettycash/pettycash',
#             'objects': http.request.env['pettycash.pettycash'].search([]),
#         })

#     @http.route('/pettycash/pettycash/objects/<model("pettycash.pettycash"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pettycash.object', {
#             'object': obj
#         })
