# -*- coding: utf-8 -*-
# © 2017 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.multi
    def _prepare_sale_line(self, line, fiscal_position):
        sale_line = super(SaleSubscription, self)._prepare_sale_line(line, fiscal_position)
        sale_line['page_break'] = line.page_break
        return sale_line

    @api.multi
    def _prepare_invoice_line(self, line, fiscal_position):
        invoice_line = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position)
        invoice_line['page_break'] = line.page_break
        return invoice_line


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    page_break = fields.Boolean(
        string="Page Break",
        help="Do a page break after this")