# -*- coding: utf-8 -*-

import base64

from odoo.http import content_disposition, Controller, request, route
import odoo.addons.portal.controllers.portal as PortalController
from datetime import date, datetime
import base64
import io
from werkzeug.utils import redirect
from odoo import http
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from odoo.tools.translate import _
import pytz
import time
from odoo.tools import formataddr



class ESSPortal(Controller):

    def check_modules(self):
        values = {}
        if request.env['ir.module.module'].sudo().search([('name', '=', 'loan')]).state == 'installed':
            values.update({
                'loan': True,
            })
        else:
            values.update({
                'loan': False,
            })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_expense')]).state == 'installed':
            values.update({
                'expense': True,
            })
        else:
            values.update({
                'expense': False,
            })
        
        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_payroll')]).state == 'installed':
            values.update({
                'payslip': True,
            })
        else:
            values.update({
                'payslip': False,
            })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'employee_documents_expiry')]).state == 'installed':
            values.update({
                'documents': True,
            })
        else:
            values.update({
                'documents': False,
            })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_holidays')]).state == 'installed':
            values.update({
                'holidays': True,
            })
        else:
            values.update({
                'holidays': False,
            })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'Employee_Training')]).state == 'installed':
            values.update({
                'training': True,
            })
        else:
            values.update({
                'training': False,
            })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_employee_letter')]).state == 'installed':
            values.update({
                'letter': True,
            })
        else:
            values.update({
                'letter': False,
            })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'pettycash')]).state == 'installed':
            values.update({
                'pettycash': True,
            })
        else:
            values.update({
                'pettycash': False,
            })
        
        if request.env['ir.module.module'].sudo().search([('name', '=', 'project')]).state == 'installed':
            values.update({
                'av_project': True,
            })
        else:
            values.update({
                'av_project': False,
            })
        
        if request.env['ir.module.module'].sudo().search([('name', '=', 'documents')]).state == 'installed':
            values.update({
                'company_documents': True,
            })
        else:
            values.update({
                'company_documents': False,
            })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_payslip_correction')]).state == 'installed':
            values.update({
                'hr_payslip_correction': True,
            })
        else:
            values.update({
                'hr_payslip_correction': False,
            })


        return values

    @route(['/attachment/download'], type='http', auth='public')
    def download_attachment(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"]
        )
        print(attachment)

        if attachment:
            attachment = attachment[0]

            if attachment["type"] == "url":
                if attachment["url"]:
                    return redirect(attachment["url"])
                else:
                    return request.not_found()
            elif attachment["datas"]:
                data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
                return http.send_file(data, filename=attachment['name'], as_attachment=True)
            else:
                return request.not_found()


        print(attachment)

    @route(['/my', '/my/dashboard'], type='http', auth='user', website=True)
    def dashboard(self, redirect=None, **post):
        values = {}
        leave_allocation_list = []
        leave_list = []
        appraisal_list = []
        announcement_list = []
        attendance_list = []

        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        
        values = self.check_modules()


        values.update({
            'error': {},
            'error_message': [],
        })

        
        

        douc_obj = []
        if request.env['ir.module.module'].sudo().search([('name', '=', 'employee_documents_expiry')]).state == 'installed':
            douc_obj = request.env['hr.employee.document'].sudo().search([('employee_ref','=',emb_obj.id)])

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_holidays')]).state == 'installed':
            leave_type = request.env['hr.leave.type'].sudo().search([]).with_context(employee_id=emb_obj.id)
            for le in leave_type:
                if le.allocation_type == 'fixed':
                    leave_allocation_list.append({
                            'name': le.name,
                            'value': le.virtual_remaining_leaves,
                            'unit': (_(' hours') if le.request_unit == 'hour' else _(' days')),
                        })
        
        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_appraisal')]).state == 'installed':
            appraisal_obj = request.env['hr.appraisal'].sudo().search([('employee_id','=',emb_obj.id)])
            for app in appraisal_obj:
                appraisal_list.append({
                    'date': app.date_close,
                    'state': app.state,
                })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_reward_warning')]).state == 'installed':
            announcement_obj = request.env['hr.announcement'].sudo().search([('state','=','approved')])
            for ann in announcement_obj:
                announcement_list.append({
                    'title': ann.announcement_reason,
                    'date_start': ann.date_start,
                    'date_end': ann.date_end,
                })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_attendance')]).state == 'installed':
            attendance_obj = request.env['hr.attendance'].sudo().search([('employee_id','=',emb_obj.id)],order="id desc",limit=5)
            for att in attendance_obj:
                attendance_list.append({
                    'date': att.check_in.date(),
                    'in': att.check_in.time(),
                    'out': att.check_out.time(),
                })
        
        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_holidays')]).state == 'installed':
            leave_obj = request.env['hr.leave'].sudo().search([('employee_id','=',emb_obj.id)])
            for leave in leave_obj:
                leave_list.append({
                    'name': leave.holiday_status_id.name,
                    'state': leave.state,
                    'number_of_days':leave.number_of_days,
                })



        values.update({
            'partner': partner,
            'employee': emb_obj,
            'leave_allocation_list': leave_allocation_list,
            'appraisal_list': appraisal_list,
            'announcement_list': announcement_list,
            'attendance_list': attendance_list,
            'leave_list': leave_list,
            'douc_exp_obj': self.get_expiry_douc(douc_obj),
            'douc_obj': douc_obj,
        })
        

        response = request.render("ess.ess_dashboard", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/leaves'], type='http', auth='user', website=True)
    def leaves(self, redirect=None, **post):
        values = {}
        leave_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        leave_type = request.env['hr.leave.type'].sudo().search([])
        leave_obj = request.env['hr.leave'].sudo().search([('employee_id','=',emb_obj.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #error, error_message = self.details_form_validate(post)
            post.update({
                'employee_id': emb_obj.id,
                'holiday_status_id': int(post['holiday_status_id']),
            })
            request.env['hr.leave'].sudo().create(post)

            
        for leave in leave_obj:
            leave_list.append({
                'name': leave.holiday_status_id.name,
                'state': leave.state,
                'number_of_days':leave.number_of_days,
            })


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'leave_type': leave_type.with_context(employee_id=emb_obj.id),
            'leave_list': leave_list,
        })


        response = request.render("ess.ess_leaves", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/history_leaves'], type='http', auth='user', website=True)
    def history_leaves(self, redirect=None, **post):
        values = {}
        leave_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        leave_obj = request.env['hr.leave'].sudo().search([('employee_id','=',emb_obj.id), ('state','=', 'validate')])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })
            
        for leave in leave_obj:
            leave_list.append({
                'name': leave.holiday_status_id.name,
                'state': leave.state,
                'number_of_days':leave.number_of_days,
            })


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'leave_obj': leave_obj,
            'leave_list': leave_list,
        })


        response = request.render("ess.ess_history_leaves", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/track_leaves'], type='http', auth='user', website=True)
    def track_leaves(self, redirect=None, **post):
        values = {}
        leave_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        leave_obj = request.env['hr.leave'].sudo().search([('employee_id','=',emb_obj.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

            
        for leave in leave_obj:
            leave_list.append({
                'name': leave.holiday_status_id.name,
                'state': leave.state,
                'number_of_days':leave.number_of_days,
            })


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'leave_list': leave_list,
        })


        response = request.render("ess.ess_track_leaves", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/short_leaves'], type='http', auth='user', website=True)
    def short_leaves(self, redirect=None, **post):
        values = {}
        leave_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        leave_type = request.env['hr.leave.type'].sudo().search([('request_unit', '=', 'hour')])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #error, error_message = self.details_form_validate(post)
            post.update({
                'employee_id': emb_obj.id,
                'holiday_status_id': int(post['holiday_status_id']),
            })
            request.env['hr.leave'].sudo().create(post)

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'leave_type': leave_type.with_context(employee_id=emb_obj.id),
            # 'leave_list': leave_list,
        })


        response = request.render("ess.ess_short_leaves", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/leaves_balance'], type='http', auth='user', website=True)
    def leaves_balance(self, redirect=None, **post):
        values = {}
        leave_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        leave_type = request.env['hr.leave.type'].sudo().search([])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'leave_type': leave_type.with_context(employee_id=emb_obj.id),
        })


        response = request.render("ess.ess_balance_leaves", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/loan'], type='http', auth='user', website=True)
    def loan(self, redirect=None, **post):
        values = {}
        loan_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #error, error_message = self.details_form_validate(post)
            post.update({
                'employee_id': emb_obj.id,
            })
            loan = request.env['hr.loan'].sudo().create(post)
            loan.compute_installment()

            

        loan_obj = request.env['hr.loan'].sudo().search([('employee_id','=',emb_obj.id)])


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'loan_obj': loan_obj,
            #'leave_list': leave_list,
        })
        
        print(values)
        response = request.render("ess.ess_loan", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/loan_report'], type='http', auth='user', website=True)
    def loan_report(self, redirect=None, **post):
        values = {}
        loan_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        loan_obj = request.env['hr.loan'].sudo().search([('employee_id','=',emb_obj.id), ('state', '=', 'approve')])


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'loan_obj': loan_obj,
        })
        
        response = request.render("ess.ess_loan_report", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/track_loan'], type='http', auth='user', website=True)
    def track_loan(self, redirect=None, **post):
        values = {}
        loan_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        loan_obj = request.env['hr.loan'].sudo().search([('employee_id','=',emb_obj.id)])


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'loan_obj': loan_obj,
        })
        
        response = request.render("ess.ess_track_loan", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/installments_loan'], type='http', auth='user', website=True)
    def installments_loan(self, redirect=None, **post):
        values = {}
        loan_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        loan_obj = request.env['hr.loan'].sudo().search([('employee_id','=',emb_obj.id)])


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'loan_obj': loan_obj,
        })
        
        response = request.render("ess.ess_installments_loan", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/allocation'], type='http', auth='user', website=True)
    def allocation(self, redirect=None, **post):
        values = {}
        allocation_list = []
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        leave_type = request.env['hr.leave.type'].sudo().search([])
        allocation_obj = request.env['hr.leave.allocation'].sudo().search([('employee_id','=',emb_obj.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #error, error_message = self.details_form_validate(post)

            leav_type = request.env['hr.leave.type'].browse(int(post['holiday_status_id']))
            if leav_type.request_unit == 'day':
                post.update({
                    'number_of_days_display': post['duration'],
                })
            else:
                post.update({
                    'number_of_hours_display': post['duration'],
                })
            post.update({
                'employee_id': emb_obj.id,
                'holiday_status_id': int(post['holiday_status_id']),
                'number_of_days': post['duration'],
            })
            post.pop('duration')
            request.env['hr.leave.allocation'].sudo().create(post)

            
        for leave in allocation_obj:
            allocation_list.append({
                'name': leave.holiday_status_id.name,
                'state': leave.state,
                'number_of_days':leave.number_of_days,
                'last_allocation_date':leave.last_allocation_date,
                'allocated_until':leave.allocated_until,
                'expiry_date':leave.expiry_date,
                'available_from':leave.available_from,
            })


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'leave_type': leave_type.with_context(employee_id=emb_obj.id),
            'allocation_list': allocation_list,
        })
        

            
        response = request.render("ess.ess_allocation", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/document'], type='http', auth='user', website=True)
    def document(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        doc_type = request.env['document.type'].sudo().search([])
        
        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #error, error_message = self.details_form_validate(post)

            if 'document_type' in post:
                post.update({
                    'document_type': int(post['document_type']),
                })

            name = post.get('doc_attachment_id').filename
            file = post.get('doc_attachment_id')

            post.pop("doc_attachment_id")


            post.update({
                'employee_ref': emb_obj.id,
            })


            docid = request.env['hr.employee.document'].sudo().create(post)

            Attachments = request.env['ir.attachment']
            
            attachment_id = Attachments.sudo().create({
                'name': name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'res_model': 'hr.employee.document',
                'res_id': docid.id
            })

            docid.sudo().update({
                'doc_attachment_id': [(4, attachment_id.id)],
            })

        docs_obj = request.env['hr.employee.document'].sudo().search([('employee_ref','=',emb_obj.id)])

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'doc_type': doc_type,
            'docs_obj': docs_obj,
        })
        

            
        response = request.render("ess.ess_document", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/view_document'], type='http', auth='user', website=True)
    def view_document(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })
        docs_obj = request.env['hr.employee.document'].sudo().search([('employee_ref','=',emb_obj.id)])

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'docs_obj': docs_obj,
        })
        
        response = request.render("ess.ess_view_docs", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/view_my_company_document'], type='http', auth='user', website=True)
    def view_my_company_document(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })
        docs_obj = request.env['documents.document'].sudo().search([('owner_id','=',request.env.user.id)])

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'docs_obj': docs_obj,
        })
        
        response = request.render("ess.ess_view_company_docs_owner", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/view_my_company_requested_document'], type='http', auth='user', website=True)
    def view_my_company_requested_document(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #error, error_message = self.details_form_validate(post)


            name = post.get('attachment_id').filename
            file = post.get('attachment_id')

            post.pop("attachment_id")

            Attachments = request.env['ir.attachment']
            
            attachment_id = Attachments.sudo().create({
                'name': name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'res_model': 'documents.document',
                'res_id': int(post['id'])
            })
            
            doc_id = request.env['documents.document'].sudo().browse([int(post['id'])])
            doc_id.sudo().write({
                'attachment_id': attachment_id.id,
            })


        docs_obj = request.env['documents.document'].sudo().search([('create_uid','!=',request.env.user.id), ('owner_id','=',request.env.user.id)])

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'docs_obj': docs_obj,
        })
        
        response = request.render("ess.ess_view_company_docs_req", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/document_my_request'], type='http', auth='user', website=True)
    def document_my_request(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
                
        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #error, error_message = self.details_form_validate(post)
            post.update({
                'owner_id': int(post['owner_id']),
                'partner_id': int(post['partner_id']),
                'folder_id': int(post['folder_id']),
                'activity_type_id': int(post['activity_type_id']),
                'res_model': 'documents.document',
                'create_uid': request.env.user.id,
            })


            request.env['documents.document'].sudo().create(post)

        docs_obj = request.env['documents.document'].sudo().search([('create_uid','=',request.env.user.id), ('owner_id','!=',request.env.user.id)])

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'docs_obj': docs_obj,
            'uids': request.env['res.users'].sudo().search([]),
            'partner_ids': request.env['res.partner'].sudo().search([]),
            'folder_ids': request.env['documents.folder'].sudo().search([]),
            'activity_type_ids': request.env['mail.activity.type'].sudo().search([('category', '=', 'upload_file')]),
        })
        

            
        response = request.render("ess.ess_document_my_request", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/expense'], type='http', auth='user', website=True)
    def expense(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        product_obj = request.env['product.product'].sudo().search([('can_be_expensed', '=', True)])
        

        values = self.check_modules() 

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            post.update({
                'employee_id': emb_obj.id,
                'name': request.env['product.product'].sudo().browse(int(post['product_id'])).display_name,
            })

            request.env['hr.expense'].sudo().create(post)


        expense_obj = request.env['hr.expense'].sudo().search([('employee_id', '=', emb_obj.id)])

        print(expense_obj)
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'product_obj': product_obj,
            'expense_obj': expense_obj,
        })
        

            
        response = request.render("ess.ess_expenses", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/track_expense'], type='http', auth='user', website=True)
    def track_expense(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        

        values = self.check_modules() 

        values.update({
            'error': {},
            'error_message': [],
        })


        expense_obj = request.env['hr.expense'].sudo().search([('employee_id', '=', emb_obj.id)])

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'expense_obj': expense_obj,
        })
        

            
        response = request.render("ess.ess_track_expenses", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/view_tasks'], type='http', auth='user', website=True)
    def view_tasks(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        

        values = self.check_modules() 

        values.update({
            'error': {},
            'error_message': [],
        })


        tasks_obj = request.env['project.task'].sudo().search(['|', ('user_id', '=', request.env.user.id), ('create_uid', '=', request.env.user.id)])

        values.update({
            'uid':request.env.user,
            'partner': partner,
            'employee': emb_obj,
            'tasks_obj': tasks_obj,
        })
        

            
        response = request.render("ess.ess_tasks", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/announcement'], type='http', auth='user', website=True)
    def announcement(self, redirect=None, **post):
        values = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        announcement_obj = request.env['hr.announcement'].sudo().search([('is_announcement', '=', True)])
        announcement_by_employee_obj = request.env['hr.announcement'].sudo().search([('announcement_type', '=', 'employee')]).filtered(lambda r: emb_obj in r.employee_ids)
        announcement_by_department_obj = request.env['hr.announcement'].sudo().search([('announcement_type', '=', 'department')]).filtered(lambda r: emb_obj.department_id in r.department_ids)
        announcement_by_job_obj = request.env['hr.announcement'].sudo().search([('announcement_type', '=', 'job_position')]).filtered(lambda r: emb_obj.job_id in r.position_ids)

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'announcement_obj': announcement_obj,
            'announcement_by_employee_obj': announcement_by_employee_obj,
            'announcement_by_department_obj': announcement_by_department_obj,
            'announcement_by_job_obj': announcement_by_job_obj,
        })
        
        response = request.render("ess.ess_announcement", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/eos'], type='http', auth='user', website=True)
    def eos(self, redirect=None, **post):
        values = {}
        eos_value = {}
        
        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])

        
        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            eos_value = request.env['end.of.service.award'].sudo().get_employee_end_of_service(emb_obj,
                                                                                               datetime.strptime(str(post['date']),DEFAULT_SERVER_DATE_FORMAT).date(),
                                                                                               post['type'])

        values.update({
            'partner': partner,
            'employee': emb_obj,
            'eos_value' : eos_value,
        })
        

            
        response = request.render("ess.ess_eos", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/training'], type='http', auth='user', website=True)
    def training(self, redirect=None, **post):
        values = {}
        training_list = []


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })


        if post and request.httprequest.method == 'POST':

            post.pop("duration")
            post.pop("f_date")
            post.pop("to_date")
            post.pop("trainer_id")
            post.pop("capacity")
            post.pop("price")
            post.update({
                'employee_id': emb_obj.id,
            })

            request.env['training.training'].sudo().create(post)

        training_obj = request.env['course.schedule'].sudo().search([('state','=','active')])
        for tra_obj in training_obj:
            if tra_obj.registered_employees:
                for em in tra_obj.registered_employees:
                    if em.employee_id.id == emb_obj.id:
                        training_list.append({
                            'id':tra_obj.id,
                            'course':tra_obj.course_id.course,
                            'duration':tra_obj.duration,
                            'to_date':tra_obj.to_date,
                            'f_date':tra_obj.f_date,
                            'capacity':tra_obj.capacity,
                            'price':tra_obj.price,
                            'trainer_id':tra_obj.trainer_id.partner_name.name,
                        })

        
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'training_obj': training_obj,
            'training_list': training_list,
        })
        response = request.render("ess.ess_training", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/track_training'], type='http', auth='user', website=True)
    def track_training(self, redirect=None, **post):
        values = {}
        training_list = []


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        training_obj = request.env['training.training'].sudo().search([('employee_id','=',emb_obj.id)])
        # training_obj = request.env['course.schedule'].sudo().search([('state','=','active')])
        # for tra_obj in training_obj:
        #     if tra_obj.registered_employees:
        #         for em in tra_obj.registered_employees:
        #             if em.employee_id.id == emb_obj.id:
        #                 training_list.append({
        #                     'id':tra_obj.id,
        #                     'course':tra_obj.course_id.course,
        #                     'duration':tra_obj.duration,
        #                     'to_date':tra_obj.to_date,
        #                     'f_date':tra_obj.f_date,
        #                     'capacity':tra_obj.capacity,
        #                     'price':tra_obj.price,
        #                     'trainer_id':tra_obj.trainer_id.partner_name.name,
        #                 })

        
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'training_list': training_list,
            'training_obj': training_obj,
        })
        response = request.render("ess.ess_track_training", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/my_courses_training'], type='http', auth='user', website=True)
    def my_courses_training(self, redirect=None, **post):
        values = {}
        training_list = []


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })

        training_obj = request.env['course.schedule'].sudo().search([('state','=','active')])
        for tra_obj in training_obj:
            if tra_obj.registered_employees:
                for em in tra_obj.registered_employees:
                    if em.employee_id.id == emb_obj.id:
                        training_list.append({
                            'id':tra_obj.id,
                            'course':tra_obj.course_id.course,
                            'duration':tra_obj.duration,
                            'to_date':tra_obj.to_date,
                            'f_date':tra_obj.f_date,
                            'capacity':tra_obj.capacity,
                            'price':tra_obj.price,
                            'trainer_id':tra_obj.trainer_id.partner_name.name,
                        })

        
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'training_list': training_list,
        })
        response = request.render("ess.ess_my_courses_training", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/letter'], type='http', auth='user', website=True)
    def letter(self, redirect=None, **post):
        values = {}


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })


        if post and request.httprequest.method == 'POST':

            if 'letter_type_id' in post:
                post.update({
                    'letter_type_id': int(post['letter_type_id']),
                })
            
            if emb_obj.parent_id:
                post.update({
                    'request_id': emb_obj.id,
                    'employee_id': emb_obj.parent_id,
                })
            else:
                post.update({
                    'request_id': emb_obj.id,
                    'employee_id': emb_obj.id,
                })
            print(post)
            request.env['letter.request'].sudo().create(post)

        letter_letter_obj = request.env['letter.letter'].sudo().search([])
        letter_request_obj = request.env['letter.request'].sudo().search([('request_id','=',emb_obj.id)])
        
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'letter_letter_obj': letter_letter_obj,
            'letter_request_obj': letter_request_obj,
        })
        response = request.render("ess.ess_letter", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/track_letter'], type='http', auth='user', website=True)
    def track_letter(self, redirect=None, **post):
        values = {}


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })


        letter_request_obj = request.env['letter.request'].sudo().search([('request_id','=',emb_obj.id)])
        
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'letter_request_obj': letter_request_obj,
        })
        response = request.render("ess.ess_track_letter", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/pettycash'], type='http', auth='user', website=True)
    def pettycash(self, redirect=None, **post):
        values = {}


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })


        if post and request.httprequest.method == 'POST':

            post.update({
                'name': emb_obj.id,
            })
            
            request.env['pettycash.pettycash'].sudo().create(post)

        pettycash_request_obj = request.env['pettycash.pettycash'].sudo().search([('name','=',emb_obj.id)])
        
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'pettycash_request_obj': pettycash_request_obj,
        })
        response = request.render("ess.ess_petty_cash", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/track_pettycash'], type='http', auth='user', website=True)
    def track_pettycash(self, redirect=None, **post):
        values = {}


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })


        pettycash_request_obj = request.env['pettycash.pettycash'].sudo().search([('name','=',emb_obj.id)])
        
        values.update({
            'partner': partner,
            'employee': emb_obj,
            'pettycash_request_obj': pettycash_request_obj,
        })

        response = request.render("ess.ess_track_petty_cash", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/attendance'], type='http', auth='user', website=True)
    def attendance(self, redirect=None, **post):
        values = {}
        
        attendance_list = []

        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        
        values = self.check_modules()


        values.update({
            'error': {},
            'error_message': [],
        })

        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_attendance')]).state == 'installed':
            attendance_obj = request.env['hr.attendance'].sudo().search([('employee_id','=',emb_obj.id)],order="id desc",limit=5)
            for att in attendance_obj:
                attendance_list.append({
                    'date': att.check_in.date(),
                    'in': att.check_in.time(),
                    'out': att.check_out.time(),
                    'worked_hours': att.worked_hours,
                })
        
   



        values.update({
            'partner': partner,
            'employee': emb_obj,
            'attendance_list': attendance_list,
        })
        

        response = request.render("ess.ess_view_attendance", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/appraisal'], type='http', auth='user', website=True)
    def appraisal(self, redirect=None, **post):
        values = {}
        appraisal_list = []

        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        
        values = self.check_modules()


        values.update({
            'error': {},
            'error_message': [],
        })


        
        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_appraisal')]).state == 'installed':
            appraisal_obj = request.env['hr.appraisal'].sudo().search([('employee_id','=',emb_obj.id)])
            for app in appraisal_obj:
                appraisal_list.append({
                    'date': app.date_close,
                    'state': app.state,
                })


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'appraisal_obj': appraisal_obj,
            'appraisal_list': appraisal_list,
        })
        

        response = request.render("ess.ess_view_appraisal", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/track_appraisal'], type='http', auth='user', website=True)
    def track_appraisal(self, redirect=None, **post):
        values = {}
        appraisal_list = []

        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        
        values = self.check_modules()


        values.update({
            'error': {},
            'error_message': [],
        })


        
        if request.env['ir.module.module'].sudo().search([('name', '=', 'hr_appraisal')]).state == 'installed':
            appraisal_obj = request.env['hr.appraisal'].sudo().search([('employee_id','=',emb_obj.id), ('state', '=', 'done')])


        values.update({
            'partner': partner,
            'employee': emb_obj,
            'appraisal_obj': appraisal_obj,
        })
        

        response = request.render("ess.ess_track_appraisal", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/request_appraisal'], type='http', auth='user', website=True)
    def request_appraisal(self, redirect=None, **post):
        values = {}


        partner = request.env.user.partner_id
        emb_obj = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
        

        values = self.check_modules()

        values.update({
            'error': {},
            'error_message': [],
        })


        if post and request.httprequest.method == 'POST':

            if 'employee_id' in post:
                post.update({
                    'employee_id': int(post['employee_id']),
                })
            
            emp_part = request.env['hr.employee'].browse(int(post['employee_id'])).user_id.partner_id

            subject = post['subject']
            post.pop('subject')
            appraisal = request.env['hr.appraisal'].sudo().create(post)

            ctx = {'url': '/mail/view?model=%s&res_id=%s' % ('hr.appraisal', appraisal.id), 'partner_to_name':emp_part.name}
            body = request.env['mail.template'].with_context(ctx)._render_template(request.env.ref('hr_appraisal.mail_template_appraisal_request').body_html, 'hr.appraisal', appraisal.id, post_process=True)

            mail_values = {
                'email_from': formataddr((request.env.user.name, request.env.user.email)),
                'author_id': partner.id,
                'model': None,
                'res_id': None,
                'subject': subject,
                'body_html': body,
                'auto_delete': True,
                'recipient_ids': [(4, emp_part.id)]
            }

            template = request.env.ref('mail.mail_notification_light', raise_if_not_found=False)
            template_ctx = {
                'message': request.env['mail.message'].sudo().new(dict(body=mail_values['body_html'], record_name=appraisal.display_name)),
                'model_description': 'Employee Appraisal',
                'company': request.env.user.company_id,
            }
            body = template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
            mail_values['body_html'] = request.env['mail.thread']._replace_local_links(body)

            request.env['mail.mail'].sudo().create(mail_values)

        
        values.update({
            'partner': partner,
            'employee': emb_obj,
        })
        response = request.render("ess.ess_request_appraisal", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route('/print/letter', methods=['POST', 'GET'], csrf=False, type='http', auth="user", website=True)
    def print_letter(self, **post):
        pdf = request.env.ref('hr_employee_letter.letter_report_id').sudo().render_qweb_pdf([int(post['id'])])[0]


        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    def get_expiry_douc(self, documents):
        doc_list = []
        for doc in documents:
            date_before = datetime.strptime(str(doc.expiry_date),DEFAULT_SERVER_DATE_FORMAT) + relativedelta(days=-int(doc.before_days))
            if doc.notification_type:
                if doc.notification_type == 'single':
                    if date.today() == doc.expiry_date:
                        doc_list.append(doc)

                elif doc.notification_type == 'multi':
                    if  date.today() == date_before.date() or date.today() == doc.expiry_date:
                         doc_list.append(doc)

                elif doc.notification_type == 'everyday':
                    if date.today() >= date_before.date() and date.today() == doc.expiry_date:
                         doc_list.append(doc)

                elif doc.notification_type == 'everyday_after':
                    if date.today() == date_before.date() and date.today() == doc.expiry_date:
                         doc_list.append(doc)


        return doc_list
