# -*- coding: utf-8 -*-
#
#  File: models/sales.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
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

