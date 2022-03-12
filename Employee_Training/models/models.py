# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError



class student(models.Model):
    _name = 'enrolled.student'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    student_name=fields.Many2one('course.schedule')

class training(models.Model):
    _name = 'training.training'
    _inherit = ['mail.thread']
    _rec_name = 'course_name'



    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    course_name = fields.Many2one('course.schedule', string='Course', required='1')
    price_id = fields.Float(string='Price', readonly='True', related='course_name.price')
    bio_content = fields.Text(string='Contents', readonly='True', related='course_name.bio_cont')
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True, readonly=True,
                                  states={'new': [('readonly', False)], 'hod': [('readonly', False)]},
                                  default=_default_employee)
    bio_agrement = fields.Text(string='Agreements', related='course_name.bio', readonly='True')
    state = fields.Selection(selection=[('new', 'New'), ('hod', 'HoD Approve'), ('hrman', 'HR Manager Approve'),
                                        ('approve', 'Approved'), ('close', 'Closed'), ('cancel', 'Canceled')
                                        ], default='new')
    user_id = fields.Many2one('res.users', string='User', related='employee_id.user_id', related_sudo=True,
                              default=lambda self: self.env.uid, readonly=True)





    @api.onchange("employee_id")

    def _get_cat(self):
        schedule=self.env['course.schedule']
        list1 = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).category_ids.ids
        schedule_ids=[]
        for sc in schedule.search([]):
            list2=sc.tags.ids
            match = any(map(lambda v: v in list1, list2))
            if match :
                schedule_ids.append(sc.id)
        #return {'domain': {'course_name': [('id', 'in', schedule_ids),('state', '=', 'active')]}}

    # @api.model
    # def create(self, values):
    #     company = super(training, self).create(values)
    #     company._create_function()
    #     return company
    #
    # def _create_function(self):
    #     print("hello")
    #
    #     groupObj = self.env['res.groups'].search([('name', '=', "Trainee Manager")])
    #     for i in groupObj.users:
    #         userObj = self.env['res.users'].search([('id', '=', i.id)])
    #         act_type_xmlid = 'mail.mail_activity_data_todo'
    #         date_deadline = datetime.now().strftime('%Y-%m-%d')
    #         summary = 'New Course request is created Notification'
    #         note = 'New Course request  is created, Please take follow-up.'
    #
    #         if act_type_xmlid:
    #             activity_type = self.sudo().env.ref(act_type_xmlid)
    #
    #         model_id = self.env['ir.model']._get(self._name).id
    #
    #         create_vals = {
    #             'activity_type_id': activity_type.id,
    #             'summary': summary or activity_type.summary,
    #             'automated': True,
    #             'note': note,
    #             'date_deadline': date_deadline,
    #             'res_model_id': model_id,
    #             'res_id': self.id,
    #             'user_id': userObj.id,
    #         }
    #         activities = self.env['mail.activity'].create(create_vals)





    def action_new(self):
        self.state = 'new'


    def action_hod(self):
        self.state = 'hod'


    def action_hrman(self):
        self.state = 'hrman'


    def action_approve(self):
        self.state = 'approve'


    def action_close(self):
        self.state = 'close'


    def action_cancel(self):
        self.state = 'cancel'


class CourseSchedule(models.Model):
    _name = 'course.schedule'
    _inherit = ['mail.thread' ]
    _rec_name = 'text'


    def calc_remain(self):
        if self.capacity or self.reserv:
            if self.capacity >= self.reserv:
                self.remain = self.capacity - self.reserv

    def compute_reserv(self):
        calc_reserv = self.env['training.training']
        for sch in self:
            sch.reserv = calc_reserv.search_count([('course_name.id', '=', sch.id), ('state', '!=', 'cancel'),('state', '!=', 'new')])
            if sch.reserv == sch.capacity:
                sch.write({'state': 'close'})
            elif sch.reserv < sch.capacity:
                sch.write({'state':'active'})
            return


    # @api.onchange('f_date','to_date')
    # def _calc_days(self):
    #     if self.f_date and self.to_date and self.f_date <= self.to_date:
    #         date_format = "%Y-%m-%d"
    #         start_date = datetime.strptime(self.f_date,date_format)
    #         end_date = datetime.strptime(self.to_date,date_format)
    #         res = end_date - start_date
    #         self.duration = int(res.days)


    course_id = fields.Many2one('course.training', string='Course',required='1')
    duration = fields.Integer('Duration')
    f_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    capacity = fields.Integer(string='Capacity',default=1,required=1)
    tags = fields.Many2many('hr.employee.category', 'sch_category_rel', 'sch_id', 'category_id', string='Tags')
    price = fields.Float(string='Price', related='course_id.price_ids', readonly=True)
    trainer_id = fields.Many2one('partner.trainer', string='Trainer')
    reserv = fields.Integer(string='Reservation', compute='compute_reserv')
    remain = fields.Integer(string='Remaining', compute='calc_remain')
    bio = fields.Text(string='Bio')
    state = fields.Selection(selection=[('new', 'New'), ('active', 'Active'), ('close', 'Closed')
                                        ], default='new', track_invisiblty='onchange')
    text = fields.Char(string='Cou', related='course_id.course')
    bio_cont = fields.Text('Bio', related='course_id.bio_course')
    training = fields.One2many('training.training', 'course_name', string='Train')
    registered_employees = fields.One2many('enrolled.student', 'student_name', string='Employees')


    # @api.onchange('tags')
    # def compute_reserv_emploayees_name(self):
    #     calc_reserv = self.env['training.training'].search([])
    #     for i in calc_reserv:
    #         print(i.course_id.id)
    #         print(i.employee_id.name)
            # sch.reserv = calc_reserv.search_count(
            #     [('course_name.id', '=', sch.id), ('state', '!=', 'cancel'), ('state', '!=', 'new')])
            # if sch.reserv == sch.capacity:
            #     sch.write({'state': 'close'})
            # elif sch.reserv < sch.capacity:
            #     sch.write({'state': 'active'})
            # return





    def action_new(self):
        self.state = 'new'


    def action_active(self):
        self.state = 'active'


    def action_close(self):
        self.state = 'close'


# ===============>>>>>>>>================<<<<<<<<<<<==============

class PartnerTrainer(models.Model):
    _name = 'partner.trainer'
    _inherit = ['mail.thread']
    _rec_name = 'partner_name'

    partner_name = fields.Many2one('res.partner', string='Trainer', domain=[('active', '=', True)])


# =======================>>>>>==================<<<<<==================

class CourseTraining(models.Model):
    _name = 'course.training'
    _inherit = ['mail.thread' ]
    _rec_name = 'course'

    course = fields.Char(string='Course Name',required='1')
    code = fields.Char(string='Code')
    bio_course = fields.Text('Bio')
    price_ids = fields.Float(string='Price',required='1')


    _sql_constraints = [
        ('course_code_unique',
         'UNIQUE(code)',
         'Code Must be Unique'),
    ]




class ResPartner(models.Model):
    _inherit = 'res.partner'
    active = fields.Boolean('Is a Trainer')


# ======================================================================

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    cour_ids = fields.Selection(selection=[('new', 'New')])







