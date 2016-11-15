# -*- coding: utf-8 -*-
#
#  File: models/contracts.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from lxml import etree
import simplejson
import re

from openerp import _, api, fields, models
from openerp.loglevels import ustr
from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError, AccessError

import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class EagleContractCategory(models.Model):
    _name = 'eagle.contract.category'
    _description = 'File category'
    
    # ---------- Fields management
    
    name = fields.Char(string='Category')


class EagleContractBase(models.Model):
    _name = 'eagle.contract'
    _description = 'Eagle file'
    _inherit = ['mail.thread']

    # ---------- Fields management

    name = fields.Char(string='File',
        default=lambda self: self._context.get('default_name', _('New')))

    # ---------- Eagle management

    @api.model
    def read_eagle_params(self):

        Params = self.env['eagle.config.params']
        try:
            params = Params.search([], limit=1)
        except:
            params = False

        if not params:
            return {}

        params = params.read()
        if isinstance(params, list): params = params[0]

        return params

    @api.model
    def get_eagle_param(self, param_name=None, param_default=False):

        try:
            params = self.env['eagle.config.params'].search([], limit=1)
        except:
            params = False

        try:
            return getattr(params, param_name, param_default)
        except:
            pass

        return params

    @api.multi
    def get_eagle_parameters(self):
        for params in self.env['eagle.config.params'].search([]):
            return params

        return False

    @api.model
    def get_current_tabs_profile_name(self):
        tabs_profile = False
        current_user = self.env.user
        if current_user.eagle_tabs_profile:
            tabs_profile = current_user.eagle_tabs_profile
        if not tabs_profile:
            tabs_profile = self.get_eagle_param('tabs_profile', False)

        return tabs_profile

    @api.model
    def get_current_tabs_profile(self):
        tabs_profile = self.get_current_tabs_profile_name()
        ret = False
        try:
            ret = dict.fromkeys(re.sub(r'[^;^a-z_]+', '', str(tabs_profile.opts)).split(';'), True)
        except:
            pass

        if not ret:
            raise UserError(_("Please define a tab's profile in Eagle's configuration!"))

        return ret

    # ---------- States management

    # Response to the "Set to Draft" button
    @api.multi
    def action_contract_draft(self):
        self.state = 'draft'

        return True

    # Response to the "Set to Confirm" button
    @api.multi
    def action_contract_confirm(self):

        for row in self.read(['customer_id']):
            if not row.get('customer_id', []):
                raise UserError(_('Please select a customer.'))
        self.state ='confirm'

        eagle_param = self.get_eagle_parameters()
        if not eagle_param or not eagle_param.auto_production_state or len(self._ids) < 1:
            return True

        to_do = []
        for cnt in self:
            if cnt.state == 'confirm':
                cnt.action_contract_production()

        return True

    # Response to the "Set to Production State" button
    @api.multi
    def action_contract_production(self):
        for row in self.read(['customer_id']):
            if not row.get('customer_id', []):
                raise UserError(_('Please select a customer.'))
        self.state = 'production'

        return True

    # Response to the "Set to Closed State" button
    @api.multi
    def action_contract_close(self):
        self.state = 'closed'

        return True

    # Response to the "Set to Closed State" button
    @api.multi
    def action_contract_cancel(self):
        self.state = 'canceled'

        return True

class EagleContractPos(models.Model):
    _name = 'eagle.contract.position'
    _description = 'Contract position'
    _order = 'sequence,id'
    
    def get_eagle_parameters(self):
        for params in self.env['eagle.config.params'].search([]):
            return params

        return False

    # ---------- Fields management

    @api.one
    @api.depends('is_billable', 'list_price', 'discount', 'qty')
    def _amount_line_base(self, cr, uid, line_ids, field_name, arg, context=None):

        self.cl_total = 0.0
        if self.is_billable:
            price = self.list_price
            if self.discount:
                price *= (100 - self.discount) / 100.0
            self.cl_total = price * self.qty

    @api.one
    @api.depends('state')
    def _get_is_invoicable(self):
        self.is_invoicable = (self.state != 'done')

    name = fields.Many2one('product.product', string='Product')
    qty = fields.Float('Quantity')
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    contract_id = fields.Many2one('eagle.contract', string='Contract', ondelete='cascade')
    recurrence_id = fields.Many2one('product.recurrence.unit', string='Recurrence')
    next_invoice_date = fields.Date('Next action date')
    state = fields.Selection([
                ('open','To install'),
                ('done','Installed'),
                ('recurrent','Recurrent'),
                ('progressive','Progressive'),
                ], string='State',
                default='open')
    cancellation_deadline = fields.Integer('Days before')
    is_active = fields.Boolean('Active')
    is_billable = fields.Boolean('Billable?', default=True)
    start_of_period = fields.Boolean('Start of period?')
    sequence = fields.Integer('Sequence', default=1)
    description = fields.Char('Description')
    out_description = fields.Char('Reported text', default='')
    list_price = fields.Float('Sale Price', digits=dp.get_precision('Sale Price'), help="Base price for computing the customer price.")
    cl_total = fields.Float(compute='_amount_line_base', string='Total', digits=dp.get_precision('Sale Price'))
    discount = fields.Float('Discount')
    notes = fields.Text('Notes', translate=True)
    property_ids = fields.Many2many(
        'mrp.property', 'position_property_rel', 'contract_id', 'property_id',
        string='Properties',
        copy=False)
    progr_rate = fields.Float('Rate [%]')
    progr_invoiced = fields.Boolean('Invoiced')
    is_invoicable = fields.Boolean(compute='_get_is_invoicable', string='Is invoicable?', store=True)

    product_type = fields.Selection([
        ('make_to_stock', 'from stock'),
        ('make_to_order', 'on order')],
        string='Procurement Method',
        required=True,
        default='make_to_stock',
        help="From stock: When needed, the product is taken from the stock or we wait for replenishment.\nOn order: When needed, the product is purchased or produced.")


class EagleContract(models.Model):
    _inherit = 'eagle.contract'
    _order = 'date_start desc, id desc'

    @api.model
    def _default_tab_profile_other_infos(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('other_infos', False)

    @api.model
    def _default_parm_use_members_list(self):
        params = self.read_eagle_params()
        return params.get('use_members_list', False)

    @api.model
    def _default_parm_use_partners_list(self):
        params = self.read_eagle_params()
        return params.get('use_partners_list', False)

    @api.model
    def _default_parm_use_partners_roles(self):
        params = self.read_eagle_params()
        return params.get('use_partners_roles', False)

    @api.model
    @api.depends('partners')
    def _get_partners_lists(self):
        lst_cnt = ["<li> - %s</li>" % x.comp_name for x in self.partners]
        self.cnt_partners = '\n'.join(lst_cnt)

    state = fields.Selection([
        ('draft','Offer'),
        ('confirm','Confirmation'),
        ('production','Production'),
        ('closed','Closed'),
        ('canceled','Canceled'),
        ], string='File State',
        default='draft'
    )
    positions = fields.One2many('eagle.contract.position', 'contract_id', string='Positions', copy=True)
    date_start = fields.Date('Start date', default=datetime.now().strftime('%Y-%m-%d'))
    date_end = fields.Date('End date')
    customer_id = fields.Many2one('res.partner', string='Customer', required=False, domain=[('is_company','=',True)])
    user_id = fields.Many2one('res.users', string='Salesman', readonly=True, states={'draft':[('readonly',False)]},
        default=lambda self: self.env.user)
    financial_partner_id = fields.Many2one('res.partner', string='Funded by')
    members = fields.Many2many(
        'res.users', 'eagle_contract_user_rel', 'contract_id', 'uid',
        string='File members',
        copy=False)
    partners = fields.Many2many(
        'res.partner', 'eagle_contract_partner_rel', 'contract_id', 'partner_id',
        string='File partners',
        copy=False)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get('account.account'))
    notes = fields.Text('Notes', translate=True)
    cust_ref = fields.Char('Customer reference')
    category_id = fields.Many2one('eagle.contract.category', string='File category')
    sale_partner_id = fields.Many2one('res.partner', string='Shipping to')
    cnt_partners = fields.Char(compute='_get_partners_lists', string='File partners')

    eagle_parm_use_members_list = fields.Boolean(compute='_get_eagle_params', string='Uses members list?',
        default=_default_parm_use_members_list)
    eagle_parm_use_partners_list = fields.Boolean(compute='_get_eagle_params', string='Uses partners list?',
        default=_default_parm_use_partners_list)
    eagle_parm_use_partners_roles = fields.Boolean(compute='_get_eagle_params', string='Uses partners roles list?',
        default=_default_parm_use_partners_roles)

    tab_profile_other_infos = fields.Boolean(compute='_get_tabs_profile', string='tab_profile_other_infos',
        default=_default_tab_profile_other_infos)

    @api.multi
    def _get_tabs_profile(self):
        profiles = self.get_current_tabs_profile()

        for cnt in self:
            cnt.tab_profile_other_infos = profiles.get('other_infos', False)

    # ---------- Eagle management

    @api.one
    def _get_eagle_params(self):
        params = self.read_eagle_params()
        self.eagle_parm_use_members_list = params.get('use_members_list', False)
        self.eagle_parm_use_partners_list = params.get('use_partners_list', False)
        self.eagle_parm_use_partners_roles = params.get('use_partners_roles', False)

    # ---------- Instances management

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            if self.get_eagle_param('use_cn_seq', False):
                vals['name'] = self.env['ir.sequence'].next_by_code('eagle.contract') or 'New'

        return super(EagleContract, self).create(vals)

    @api.multi
    def write(self, vals):
        for row in self.read(['state','customer_id']):
            if row['state'] not in ['production']:
                continue
            if not row.get('customer_id', []):
                if not vals.get('customer_id', False):
                    raise UserError(_('Please select a customer.'))

        return super(EagleContract, self).write(vals)

    @api.multi
    def unlink(self):
        unlink_parent_ids = []
        unlink_children_ids = []
        for contract in self:
            if contract.state not in ['draft']:
                raise UserError(_("An already confirmed file can't be deleted!"))

        return super(EagleContract, self).unlink()

    @api.one
    def copy(self, default=None):
        default = dict(default or {}, name=self.name+ _(' (copy)'), state='draft')
        return super(EagleContract, self).copy(default=defaults)

    # ---------- Interface related

    # Activate the "Contract" tabs
    @api.multi
    def button_view_contract(self):
        return True

    # Activate the "Accounting" tabs
    @api.multi
    def button_view_accounting(self):
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(EagleContract, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,submenu=False)
        eagle_param = self.get_eagle_parameters()
        if view_type != 'form': return res
        if eagle_param and hasattr(eagle_param,'close_to_draft') and eagle_param.close_to_draft:
            eview = etree.fromstring(res['arch'])
            for btn in eview.xpath("//button[@name='action_contract_draft']"):
                btn.set('states','confirm,closed,canceled')
                d = simplejson.loads(btn.get('modifiers'))
                d['invisible'] = [('state', 'not in', ['confirm', 'closed', 'canceled'])]
                btn.set('modifiers',simplejson.dumps(d))
            res['arch'] = etree.tostring(eview)

        return res

    @api.multi
    def onchange_customer(self, customer_id):
        res = { }
        if customer_id:
            cust = self.env['res.partner'].read(customer_id, ['property_product_pricelist', 'ons_hrtif_to_invoice'])
            if cust:
                if cust.get('property_product_pricelist', False):
                    res['pricelist_id'] = cust['property_product_pricelist'][0]
                if cust.get('ons_hrtif_to_invoice', False):
                    res['ons_hrtif_to_invoice'] = cust['ons_hrtif_to_invoice'][0]
        return {
            'value': res
        }

    # ---------- States management

    @api.multi
    def check_contract_items(self):
        return True

    # Response to the "Set to Confirmed State" button
    @api.multi
    def action_contract_confirm(self):
        self.check_contract_items()
        self.date_start = datetime.now().strftime('%Y-%m-%d')
        return super(EagleContract, self).action_contract_confirm()

    # Response to the "Set to Production State" button
    @api.multi
    def action_contract_production(self):
        self.check_contract_items()
        return super(EagleContract, self).action_contract_production()

class EagleCustomer(models.Model):
    _name = 'eagle.customer'
    _description = 'Customers Files'
    _auto = False
    _rec_name = 'customer'
    _order = 'customer'

    # ---------- Fields management

    customer = fields.Char('Customer', readonly=True)
    nb_contracts = fields.Integer('Files Nb', readonly=True)
    void = fields.Char('Void', size=1, readonly=True)

    # ---------- Instances management

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE OR REPLACE VIEW %s AS (
SELECT DISTINCT
 customer_id AS id, res_partner.name as customer, count(eagle_contract.id) as nb_contracts, ' ' as void
 FROM eagle_contract, res_partner
 WHERE customer_id=res_partner.id
 GROUP BY res_partner.name, customer_id
 ORDER BY res_partner.name)""" % (self._table,))
