# -*- coding: utf-8 -*-
#
#  File: models/products.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

import re

from openerp import _, api, fields, models

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

    eagle_tab_profile_prod_contracts_list = fields.Boolean(compute='check_tabs_profile', string='eagle_tab_profile_prod_contracts_list')

    @api.multi
    @api.depends('eagle_pos_ids')
    def _get_corresponding_contracts(self):
        for prod in self:
            prod.eagle_contract_ids = [x.contract_id.id for x in prod.eagle_pos_ids if x.contract_id]


    @api.multi
    def check_tabs_profile(self):
        profiles = self.env['eagle.contract'].get_current_tabs_profile()

        for prod in self:
            prod.eagle_tab_profile_prod_contracts_list = profiles.get('prod_contracts_list', False)

