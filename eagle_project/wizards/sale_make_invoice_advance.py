#
#  File: wizards/sale_make_invoice_advance.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>


from odoo import api, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if not invoice or not order or not order.contract_id:
            return invoice

        invoice.contract_id = order.contract_id
        for line in invoice.invoice_line_ids:
            line.contract_id = order.contract_id

        return invoice

    @api.multi
    def create_invoices(self):
        return super(SaleAdvancePaymentInv, self).create_invoices()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        contract_to_compare = self[0].contract_id

        if grouped == True:
            for order in self:
                if order.contract_id == contract_to_compare:
                    continue
                else:
                    return super(SaleOrder, self).action_invoice_create(grouped=False, final=final)
        return super(SaleOrder, self).action_invoice_create(grouped=grouped, final=final)
