# -*- coding: utf-8 -*-
#
#  File: models/products.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ProductRecurrenceUnit(models.Model):
    _name = 'product.recurrence.unit'
    _description = "Recurrence units for the products and the warranties"

    # ---------- Fields management

    name = fields.Char(string='Name', required=True)
    value = fields.Integer(string='Value', required=True)
    unit = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year')],
        string='Units',
        required=True)
    keep_same_day = fields.Boolean(string='Keep same day', default=False)
    
    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    recurrence_id =  fields.Many2one('product.recurrence.unit', string='Recurrence')
    eagle_pos_ids = fields.One2many('eagle.contract.position', 'name', 'Positions')
    eagle_contract_ids = fields.One2many(
        'eagle.contract',
        compute='_get_corresponding_contracts',
        string='Contracts',
        copy=False)

    @api.multi
    @api.depends('eagle_pos_ids')
    def _get_corresponding_contracts(self):
        for prod in self:
            prod.eagle_contract_ids = [x.contract_id.id for x in prod.eagle_pos_ids if x.contract_id]

