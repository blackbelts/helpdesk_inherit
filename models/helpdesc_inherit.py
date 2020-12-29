from datetime import timedelta, datetime
import xlsxwriter
from xlsxwriter.workbook import Workbook
import base64
import xlrd
from xlrd import open_workbook
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import api, fields, models
class HelpDesk(models.Model):
    _name='quoate'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(string='Ticket', track_visibility='always', required=True)
    contact_name = fields.Char('Contact Name')
    email_from = fields.Char('Email', help="Email address of the contact", index=True)
    job = fields.Char('Job')
    phone = fields.Char('Phone')
    ticket_type = fields.Selection([('personal', 'PA'),
                                    ('travel', 'Travel'), ('medical', 'Medical'), ('motor', 'Motor')],
                                   default='personal')
    sum_insured = fields.Float('Sum Insured')
    state = fields.Selection([('new', 'New'),
                              ('verified', 'Verified'),
                              ('proposal', 'Proposal'),
                              ('won', 'Won'),
                              ('canceled', 'Canceled'), ],
                             'Status', required=True, default='new', copy=False)

    user_id = fields.Many2one('res.users', string='Assigned to', track_visibility='onchange', index=True, default=False,
                              )

    active = fields.Boolean(default=True)
    source = fields.Selection([('online', 'Online'),
                               ('call', 'Call Center'),
                               ('social', 'Social Media')],
                              'Source', copy=False)

    support_team = fields.Many2one('helpdesk_lite.team', string='Team')
    state_history_ids = fields.One2many('state.history', 'quoate_ticket_id')

    def takeit(self):
        self.user_id = self.env.uid

    @api.onchange('state')
    def log_history(self):
        self.env['state.history'].create({"quoate_ticket_id": self.id, "ticket_state": self.state,
                                          "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                          "user": self.env.uid})
        if self.state == 'verified' or self.state == 'proposal':
            self.user_id = False

    @api.onchange('support_team')
    def onchange_support_team(self):
        if self.support_team:
            # filter products by seller
            user_ids = self.support_team.member_ids.ids
            return {'domain': {'user_id': [('id', 'in', user_ids)]}}
        else:
            # filter all products -> remove domain
            return {'domain': {'user_id': []}}

    # def create_application(self):
    #     form = self.env.ref('helpdesk_inherit.insurance_app_wizard')
    #     self.user = True
    #
    #     return {
    #         'name': ('Users'),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'insurance.app.wizard',
    #         # 'view_id': [(self.env.ref('smart_claim.tree_insurance_claim').id), 'tree'],
    #         'views': [(form.id, 'form')],
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #
    #         'context': {'default_contact_name': self.contact_name,
    #                     'default_phone': self.phone}
    #
    #     }

class HelpDesk(models.Model):
    _inherit = 'helpdesk_lite.stage'

class StateHistory(models.Model):
    _inherit = 'state.history'

    quoate_ticket_id = fields.Many2one('quoate', ondelete='cascade')
    ticket_state = fields.Selection([('new', 'New'),
                              ('verified', 'Verified'),
                              ('proposal', 'Proposal'),
                              ('won', 'Won'),
                              ('canceled', 'Canceled'), ],
                             'State')

class HelpDeskTicket(models.Model):
    _inherit = 'helpdesk_lite.ticket'
    complain=fields.Text('Complain')
    complain_number = fields.Char(string='Application Number', copy=False, index=True)
    source = fields.Selection([('online', 'Online'),
                               ('call', 'Call Center'),
                               ('social', 'Social Media')],
                              'Source', copy=False)
    team_id = fields.Many2one('helpdesk_lite.team', string='Complaint Types', index=True)
    name = fields.Char(string='Ticket', track_visibility='always',required=False)

    @api.model
    def create(self, vals):
            serial_no = self.env['ir.sequence'].next_by_code('comp_number')
            currentYear = datetime.today().strftime("%Y")
            currentMonth = datetime.today().strftime("%m")
            vals['name'] = 'COMP' + '/' + currentYear[2:4] + '/' + currentMonth + '/' +serial_no
            return super(HelpDeskTicket, self).create(vals)

class TicketTypes(models.Model):
     _inherit='helpdesk_lite.team'
     support_chain = fields.Many2many('res.users', string='Support Chain')
     team_support_type = fields.Selection([('personal', 'PA'),
                                    ('travel', 'Travel'), ('medical', 'Medical'), ('motor', 'Motor')],
                                   default='personal', sting='Support Type')



class TicketApi(models.Model):
    _name = 'ticket.api'
    @api.model
    def create_ticket(self, data):
        name=""
        if data.get('type')=='pa':
            name='Personal Acciedent Ticket'
        else:
            name='Travel Group Ticket'
        group_dict={5:'0-10',15:'11-18',25:'19-70'}

        ticket_id = self.env['helpdesk_lite.ticket'].create(
            {'name': name, 'contact_name': data.get('name'), 'job': data.get('job'), 'phone': data.get('phone'),
             'email_from':data.get('mail'),'ticket_type':data.get('type')})
        if data.get('group'):
            for rec in data.get('group'):
                self.env['group.ticket'].create({'size':rec['size'],'range':group_dict.get(rec['age']),'group_id':ticket_id.id})


        return ticket_id.id