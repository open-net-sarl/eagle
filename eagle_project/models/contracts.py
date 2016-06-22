# -*- coding: utf-8 -*-
#
#  File: models/contracts.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>
##############################################################################

from openerp import _, api, fields, models
import openerp.addons.decimal_precision as dp

from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
import simplejson

import logging
_logger = logging.getLogger(__name__)


class EagleContract(models.Model):
    _inherit = 'eagle.contract'

    @api.model
    def _default_tab_profile_curr_sol(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('curr_sol', False)

    @api.model
    def _default_tab_profile_past_sol(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('past_sol', False)

    @api.model
    def _default_tab_profile_sale_subscr(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('sale_subscr', False)

    @api.model
    def _default_tab_profile_sale_subscrl(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('sale_subscrl', False)

    @api.model
    def _default_tab_profile_tasks(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('tasks', False)

    @api.model
    def _default_tab_profile_an_lines(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('an_lines', False)

    current_sale_order_lines = fields.One2many('sale.order.line', 'contract_id', string='Current Sale Order Lines', domain=[('state','=','draft')])
    past_sale_order_lines = fields.One2many('sale.order.line', 'contract_id', string='Past Sale Order Lines', domain=[('state','<>','draft')])
    current_sale_orders = fields.One2many('sale.order', 'contract_id', string='Current Sale Orders', domain=[('state','=','draft')])
    past_sale_orders = fields.One2many('sale.order', 'contract_id', string='Past Sale Orders', domain=[('state','<>','draft')])
    opportunity = fields.Many2one('crm.lead', string='Opportunity', domain="[('type', '=', 'opportunity')]")

    account_out_invoices = fields.One2many('account.invoice', 'contract_id', string='Customer Invoices', domain=[('type','=','out_invoice')])
    account_in_invoices = fields.One2many('account.invoice', 'contract_id', string='Supplier Invoices', domain=[('type','=','in_invoice')])
    account_out_inv_lines = fields.One2many('account.invoice.line', 'contract_id', string='Customer Invoice Lines', domain=[('invoice_id.type','=','out_invoice')])
    account_in_inv_lines = fields.One2many('account.invoice.line', 'contract_id', string='Supplier Invoice Lines', domain=[('invoice_id.type','=','in_invoice')])

    sale_subscriptions = fields.One2many('sale.subscription', 'eagle_contract', string='Sale Subscriptions')
    sale_subscription_line = fields.One2many('sale.subscription.line', 'eagle_contract', string='Sale Subscription Lines')

    project_tasks = fields.One2many('project.task', 'eagle_contract', string='Tasks')
    analytic_lines = fields.One2many('account.analytic.line', 'eagle_contract', string='Analytic Lines')

    tab_profile_curr_sol = fields.Boolean(compute='_get_tabs_profile', string='tab_profile_curr_sol',
                                          default=_default_tab_profile_curr_sol)
    tab_profile_past_sol = fields.Boolean(compute='_get_tabs_profile', string='tab_profile_past_sol',
                                          default=_default_tab_profile_past_sol)
    tab_profile_sale_subscr = fields.Boolean(compute='_get_tabs_profile', string='tab_profile_sale_subscr',
                                              default=_default_tab_profile_sale_subscr)
    tab_profile_sale_subscrl = fields.Boolean(compute='_get_tabs_profile', string='tab_profile_sale_subscrl',
                                              default=_default_tab_profile_sale_subscrl)
    tab_profile_tasks = fields.Boolean(compute='_get_tabs_profile', string='tab_profile_tasks',
                                              default=_default_tab_profile_tasks)
    tab_profile_an_lines = fields.Boolean(compute='_get_tabs_profile', string='tab_profile_an_lines',
                                              default=_default_tab_profile_an_lines)

    tasks_count = fields.Integer(compute='_get_tasks_count', string='Tasks count', default=0)
    leads_count = fields.Integer(compute='_get_leads_count', string='Leads count', default=0)
    sales_count = fields.Integer(compute='_get_sales_count', string='Sales count', default=0)
    invoices_count = fields.Integer(compute='_get_invoices_count', string='Invoices count', default=0)
    picks_count = fields.Integer(compute='_get_pickings_count', string='Pickings count', default=0)

    @api.multi
    def _get_tasks_count(self):
        for cnt in self:
            cnt.tasks_count = 0 if not self.id else len(self.env['project.task'].search([('eagle_contract','=',self.id)]))

    @api.multi
    def _get_leads_count(self):
        for cnt in self:
            cnt.leads_count = 1 if self.opportunity else 0

    @api.multi
    def _get_pickings_count(self):
        for cnt in self:
            cnt.picks_count = 0
            proc_grp = []
            for sale in self.env['sale.order'].search([('contract_id', 'in', [x.id for x in self])]):
                if not sale.procurement_group_id:
                    continue
                if sale.procurement_group_id.id not in proc_grp:
                    proc_grp.append(sale.procurement_group_id.id)

            if proc_grp:
                cnt.picks_count = len(self.env['stock.picking'].search([('group_id', 'in', proc_grp)]))

    @api.multi
    def _get_sales_count(self):
        for cnt in self:
            cnt.sales_count = 0 if not self.id else len(self.env['sale.order'].search([('contract_id','=',self.id)]))

    @api.multi
    def _get_invoices_count(self):
        for cnt in self:
            cnt.invoices_count = 0 if not self.id else len(self.env['account.invoice'].search([('contract_id','=',self.id)]))

    @api.multi
    def _get_tabs_profile(self):
        super(EagleContract, self)._get_tabs_profile()
        profiles = self.get_current_tabs_profile()

        for cnt in self:
            cnt.tab_profile_curr_sol = profiles.get('curr_sol', False)
            cnt.tab_profile_past_sol = profiles.get('past_sol', False)
            cnt.tab_profile_sale_subscr = profiles.get('sale_subscr', False)
            cnt.tab_profile_sale_subscrl = profiles.get('sale_subscrl', False)
            cnt.tab_profile_tasks = profiles.get('tasks', False)
            cnt.tab_profile_an_lines = profiles.get('an_lines', False)

    # ---------- UI management

    @api.multi
    def action_contract2task(self):
        tasks_ids = [t.id for t in self.env['project.task'].search([('eagle_contract', 'in', [x.id for x in self])])]
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('project.view_task_tree2')
        form_view_id = imd.xmlid_to_res_id('eagle_contract.eagle_view_task_work_form')
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "in", tasks_ids]],
            "context": {"create": False},
            "name": _("Tasks"),
        }

    @api.multi
    def action_contract2lead(self):
        leads_ids = [self.opportunity.id] if self.opportunity.id else []
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('crm.crm_case_tree_view_leads')
        form_view_id = imd.xmlid_to_res_id('eagle_contract.eagle_view_crm_opport_form_inherit')
        return {
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "in", leads_ids]],
            "context": {"create": False},
            "name": _("Opportunities"),
        }

    @api.multi
    def action_contract2invoice(self):
        invoice_ids = [i.id for i in self.env['account.invoice'].search([('contract_id', 'in', [x.id for x in self])])]
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "in", invoice_ids]],
            "context": {"create": False},
            "name": _("Invoices"),
        }

    @api.multi
    def action_contract2sale(self):
        sale_ids = [s.id for s in self.env['sale.order'].search([('contract_id', 'in', [x.id for x in self])])]
        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        form_view_id = imd.xmlid_to_res_id('eagle_contract.eagle_view_so_form_inherit')
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "in", sale_ids]],
            "context": {"create": False},
            "name": _("Sales"),
        }

    @api.multi
    def action_contract2pick(self):
        proc_grp = []
        for sale in self.env['sale.order'].search([('contract_id', 'in', [x.id for x in self])]):
            if not sale.procurement_group_id:
                continue
            if sale.procurement_group_id.id not in proc_grp:
                proc_grp.append(sale.procurement_group_id.id)

        pick_ids = []
        if proc_grp:
            pick_ids = [s.id for s in self.env['stock.picking'].search([('group_id', 'in', proc_grp)])]

        imd = self.env['ir.model.data']
        list_view_id = imd.xmlid_to_res_id('stock.vpicktree')
        form_view_id = imd.xmlid_to_res_id('stock.view_picking_form')
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "in", pick_ids]],
            "context": {"create": False},
            "name": _("Pickings"),
        }

    @api.multi
    def action_contract_confirm(self):
        ret = super(EagleContract, self).action_contract_confirm()
        if ret:
            for cnt in self:
                for sale_sub in cnt.sale_subscriptions:
                    if sale_sub.state == 'draft':
                        sale_sub.set_open()

                    if sale_sub.state == 'open':
                        sale_sub.action_recurring_invoice()

        return ret


class EagleContractPos(models.Model):
    _inherit = 'eagle.contract.position'

    # ---------- Fields management

    @api.one
    @api.depends('list_price', 'discount', 'qty', 'tax_id', 'is_billable')
    def _comp_amount_line_prj(self):
        self.cl_amount = 0.0
        self.cl_total = 0.0
        self.cl_taxes = 0.0

        tax_obj = self.env['account.tax']
        fpos_obj = self.env['account.fiscal.position']

        if self.is_billable:
            price = self.list_price
            if self.discount:
                price *= (100 - self.discount) / 100.0
            
            tax = self.tax_id
            if self.contract_id.fiscal_position:
                tax = self.contract_id.fiscal_position.map_tax([self.name.taxes_id])
            if tax:
                taxes = tax.compute_all(price, self.qty, product=self.name, partner=self.contract_id.customer_id)
                self.cl_amount = taxes['total']
                self.cl_total = taxes['total_included']
            else:
                self.cl_amount = price * self.qty
                self.cl_total = self.cl_amount

            cur = self.contract_id.pricelist_id and self.contract_id.pricelist_id.currency_id or False
            if cur:
                self.cl_amount = cur.round(self.cl_amount)
                self.cl_total = cur.round(self.cl_total)
            
            self.cl_taxes = self.cl_total - self.cl_amount

    @api.one
    def _comp_start_date(self):
        res = {}
        
        start_date = False
        if self.stock_disposal_date:
            ds = datetime.strptime(self.stock_disposal_date, '%Y-%m-%d')
            start_date = (ds + relativedelta(days=-self.product_duration)).strftime('%Y-%m-%d')
        
        self.cl_start_date = start_date

    cl_amount = fields.Float(string='Tax-free Amount', digits=dp.get_precision('Sale Price'), store=False, readonly=True, compute='_comp_amount_line_prj')
    cl_taxes = fields.Float(string='Tax Amount', digits=dp.get_precision('Sale Price'), store=False, readonly=True, compute='_comp_amount_line_prj')
    cl_total = fields.Float(string='Total', digits_compute=dp.get_precision('Sale Price'), store=False, readonly=True, compute='_comp_amount_line_prj')

    tax_id = fields.Many2many('account.tax', 'eagle_contrat_line_tax', 'cnt_line_id', 'tax_id', 'Taxes')

    cust_delivery_date = fields.Date(string='Customer Delivery Date')
    stock_disposal_date = fields.Date(string='Stock Disposal Date')
    product_duration = fields.Integer(string='Duration')
    cl_start_date = fields.Date(compute='_comp_start_date', string='Start date')

