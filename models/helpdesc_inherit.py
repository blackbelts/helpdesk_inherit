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
                              ('proposal', 'Proposal'),
                              ('won', 'Won'),
                              ('canceled', 'Canceled'), ],
                             'Status', required=True, default='new', copy=False)
    user_id = fields.Many2one('res.users', string='Assigned to', track_visibility='onchange', index=True, default=False)
    active = fields.Boolean(default=True)



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
class HelpDesk(models.Model):
    _inherit = 'helpdesk_lite.ticket'
    complain=fields.Text('Complain')




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