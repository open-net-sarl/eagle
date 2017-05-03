# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api

#Import logger
import logging
#Get the logger
_logger = logging.getLogger(__name__)

class SaleSubscriptionTemplate(models.Model):
    _inherit = 'sale.subscription.template'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    recurring_generates = fields.Selection([
        ('invoice', 'An invoice'),
        ('sale', 'A sale'),
    ],
    'Generates',
    default='invoice')