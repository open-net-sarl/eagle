#
#  File: wizards/sale_make_invoice_advance.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>


from openerp import api, models, _


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
