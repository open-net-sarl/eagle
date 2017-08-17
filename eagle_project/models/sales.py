# -*- coding: utf-8 -*-
#
#  File: models/sales.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2010-TODAY Open-Net Ltd. <http://www.open-net.ch>

from odoo import models, fields, api
from lxml import etree

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    move_ids = fields.One2many(
        'stock.move',
        related='picking_ids.move_lines',
        string='Related stock moves'
    )
    
    contract_id = fields.Many2one('eagle.contract', string='File')

    # ---------- Utils

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if not invoice_vals:
            return invoice_vals
        
        invoice_vals.update({'contract_id':self.contract_id.id})
    
        return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    contract_id = fields.Many2one('eagle.contract', string='File')
    date_order = fields.Datetime(string='Order Date', related='order_id.date_order')

    short_descr = fields.Char(string='Short descr.')
    product_type = fields.Selection(related='product_id.type', string='Product type')
    recurring_rule_type = fields.Selection(related='product_id.recurring_rule_type', string='Type de recurrence')


    # ---------- Utils

    @api.multi
    def _prepare_invoice_line(self, qty):
        invoice_line_vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if not invoice_line_vals:
            return invoice_line_vals

        invoice_line_vals.update({'contract_id':self.contract_id.id})

        return invoice_line_vals

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(group_id=group_id)
        if self.contract_id:
            vals['eagle_contract'] = self.contract_id.id

        return vals

    @api.onchange('product_id')
    def product_id_change(self):
        company_id = self.env.user.company_id.id
        pricelist_id = None
        for sol in self:
            res = super(SaleOrderLine, sol).product_id_change()
            if sol.product_id:
                contract = sol.contract_id
                if contract:
                    company_id = contract.company_id.id
                    pricelist_id = contract.pricelist_id.id

                ctx = dict(sol.env.context, company_id=company_id, force_company=company_id, pricelist=pricelist_id, quantity=sol.product_uom_qty)
                prod = sol.env['product.product'].with_context(ctx).browse(sol.product_id.id)
                sol.short_descr = prod.display_name

        return res

    @api.model
    def default_get(self, default_fields):
        values = super(SaleOrderLine, self).default_get(default_fields)
        if self.env.context.get('default_contract_id'):
            so = self.env['sale.order'].search([('contract_id','=',self.env.context['default_contract_id']),('state','in',['draft','sent','sale'])],limit=1)
            if so:
                values['order_id'] = so.id

        return values

    @api.model
    def create(self, vals):
        if not vals.get('order_id'):
            if vals.get('contract_id'):
                contract = self.env['eagle.contract'].browse(vals['contract_id'])
                if contract:
                    sale_vals = {
                        'contract_id': vals['contract_id'],
                        'partner_id': contract.customer_id.id or False,
                        'project_id': contract.default_analytic_acc.id or False
                    }
                    new_sale = self.env['sale.order'].create(sale_vals)
                    vals['order_id'] = new_sale.id

        return super(SaleOrderLine, self).create(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrderLine, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        if view_type != 'form':
            return res

        product_type = self.env.context.get('ons_product_type','')
        domain = []
        if product_type == 'service':
            domain = [('type', '=', 'service')]
        elif product_type == 'deliverable':
            domain = [('type', 'in', ['product','consu'])]
        if domain:
            eview = etree.fromstring(res['arch'])
            for node in eview.xpath("//field[@name='product_id']"):
                node.attrib['domain'] = str(domain)
            res['arch'] = etree.tostring(eview)

        return res

