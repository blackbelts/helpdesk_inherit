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
    _inherit = 'helpdesk_lite.ticket'

    job = fields.Char('Job')
    phone = fields.Char('Phone')
    ticket_type = fields.Selection([('personal', 'PA'),
                                    ('travel', 'Travel'), ('medical', 'Medical'), ('motor', 'Motor')],
                                   default='pa')
    sum_insured = fields.Float('Sum Insured')

    def create_application(self):
        print('Write Method')

class HelpDesk(models.Model):
    _inherit = 'helpdesk_lite.stage'

class HelpGroup(models.Model):
        _name = 'group.ticket'
        range=fields.Char('Range')
        size=fields.Float('Size')
        group_id=fields.Many2one('helpdesk_lite.ticket',string='ticket')


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