# -*- coding: utf-8 -*-
#
#  File: models/contracts.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>
##############################################################################

from odoo import _, api, fields, models
import odoo.addons.decimal_precision as dp

from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta
import simplejson

import logging
_logger = logging.getLogger(__name__)


class EagleContract(models.Model):
    _inherit = 'eagle.contract'

    current_sale_order_lines = fields.One2many(comodel_name='sale.order.line', inverse_name='contract_id', string='Current Sale Order Lines', domain=[('state','=','draft')])
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

    tasks_count = fields.Integer(compute='_get_tasks_count', string='Tasks count', default=0)
    leads_count = fields.Integer(compute='_get_leads_count', string='Leads count', default=0)
    sales_count = fields.Integer(compute='_get_sales_count', string='Sales count', default=0)
    invoices_count = fields.Integer(compute='_get_invoices_count', string='Invoices count', default=0)
    picks_count = fields.Integer(compute='_get_pickings_count', string='Pickings count', default=0)

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')

    lines_not_recurring = fields.One2many(
        related="sale_subscription_line", 
        domain="[('recurring_rule_type','=','none'), ('is_active','=','True')]")
    lines_recurring = fields.One2many(
        related="sale_subscription_line", 
        domain="[('recurring_rule_type','!=','none'), ('is_active','=','True')]")

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

    # ---------- UI management

    @api.multi
    def action_contract2task(self):
        tasks_ids = [t.id for t in self.env['project.task'].search([('eagle_contract', 'in', [x.id for x in self])])]
        list_view_id = self.env.ref('project.view_task_tree2').id
        form_view_id = self.env.ref('eagle_project.eagle_view_task_work_form').id
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
        list_view_id = self.env.ref('crm.crm_case_tree_view_leads').id
        form_view_id = self.env.ref('eagle_project.eagle_view_crm_opport_form_inherit').id
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
        list_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id
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
        list_view_id = self.env.ref('sale.view_order_tree').id
        form_view_id = self.env.ref('eagle_project.eagle_view_so_form_inherit').id
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "in", sale_ids]],
            "context": {"create": False, 'show_sale':True},
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

        list_view_id = self.env.ref('stock.vpicktree').id
        form_view_id =self.env.ref('stock.view_picking_form').id
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[list_view_id, "tree"], [form_view_id, "form"]],
            "domain": [["id", "in", pick_ids]],
            "context": {"create": False},
            "name": _("Pickings"),
        }

    # ---------- States management

    # Response to the "Set to Closed State" button
    @api.multi
    def action_contract_close(self):
        ret = super(EagleContract, self).action_contract_close()
        for cnt in self:
            if cnt.sale_subscription_line:
                cnt.sale_subscription_line.write({'is_active': False})

        return ret


class EagleContractPos(models.Model):
    _inherit = 'eagle.contract.position'

    # ---------- Fields management

    @api.multi
    @api.depends('list_price', 'discount', 'qty', 'tax_id', 'is_billable')
    def _comp_amount_line_prj(self):

        for pos in self:
            pos.cl_amount = 0.0
            pos.cl_total = 0.0
            pos.cl_taxes = 0.0

            tax_obj = pos.env['account.tax']
            fpos_obj = pos.env['account.fiscal.position']

            if pos.is_billable:
                price = pos.list_price
                if pos.discount:
                    price *= (100 - pos.discount) / 100.0
                
                tax = pos.tax_id

                if tax:
                    taxes = tax.compute_all(price, pos.qty, product=pos.name, partner=pos.contract_id.customer_id)
                    pos.cl_amount = taxes['total']
                    pos.cl_total = taxes['total_included']
                else:
                    pos.cl_amount = price * pos.qty
                    pos.cl_total = pos.cl_amount

                cur = pos.contract_id.pricelist_id and pos.contract_id.pricelist_id.currency_id or False
                if cur:
                    pos.cl_amount = cur.round(pos.cl_amount)
                    pos.cl_total = cur.round(pos.cl_total)
                
                pos.cl_taxes = pos.cl_total - pos.cl_amount

    @api.multi
    def _comp_start_date(self):
        res = {}
        
        for pos in self:
            start_date = False
            if pos.stock_disposal_date:
                ds = datetime.strptime(pos.stock_disposal_date, '%Y-%m-%d')
                start_date = (ds + relativedelta(days=-pos.product_duration)).strftime('%Y-%m-%d')
            
            pos.cl_start_date = start_date

    cl_amount = fields.Float(string='Tax-free Amount', digits=dp.get_precision('Sale Price'), store=False, readonly=True, compute='_comp_amount_line_prj')
    cl_taxes = fields.Float(string='Tax Amount', digits=dp.get_precision('Sale Price'), store=False, readonly=True, compute='_comp_amount_line_prj')
    cl_total = fields.Float(string='Total', digits_compute=dp.get_precision('Sale Price'), store=False, readonly=True, compute='_comp_amount_line_prj')

    tax_id = fields.Many2many('account.tax', 'eagle_contrat_line_tax', 'cnt_line_id', 'tax_id', 'Taxes')

    cust_delivery_date = fields.Date(string='Customer Delivery Date')
    stock_disposal_date = fields.Date(string='Stock Disposal Date')
    product_duration = fields.Integer(string='Duration')
    cl_start_date = fields.Date(compute='_comp_start_date', string='Start date')
