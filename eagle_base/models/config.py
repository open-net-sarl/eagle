# -*- coding: utf-8 -*-
#
#  File: config/config.py
#  Module: eagle_base
#  Eagle's config management
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#   Starting with the version 5.0, Eagle's parameters are not any more managed
#   using the old, classic way, but rather through OE V7 configuration management:
#   Each time the settings are saved, Eagle's parameters are stored.
#
#  Copyright (c) 2011-TODAY Open-Net Ltd. <http://www.open-net.ch>

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class EagleConfigParams(models.Model):
    _name = 'eagle.config.params'
    _description = 'Eagle Configuration Parameters'
    
    # ---------- Fields management

    name = fields.Char(
        string='Name',
        default='Eagle Parameters'
    )
    use_members_list = fields.Boolean(
        string='Uses members list',
        default=False
    )
    use_partners_list = fields.Boolean(
        string='Uses partners list',
        default=False
    )
    auto_production_state = fields.Boolean(
        string="Automatic 'Production state' mode?",
        default=True
    )
    close_to_draft = fields.Boolean(
        string="Can re-open a contract?"
    )
    use_cn_seq = fields.Boolean(
        string="Use the contract sequences",
        default=False
    )
    date_format = fields.Char(
        string='Customized date format',
        default='%d.%m.%Y'
    )


class EagleConfigSettings(models.TransientModel):
    _name = 'eagle.config.settings'
    _inherit = 'res.config.settings'

    @api.model
    def _get_default_val(self, field_name):
        val = False
        eagle_config_params = self.env['eagle.config.params']
        line = eagle_config_params.search([])
        if line.exists():
            val = getattr(line[0], field_name)
        return val

    # ---------- Fields management

    name = fields.Char(string='Name', default='Eagle Parameters')
    use_members_list = fields.Boolean(
        string='Uses members list',
        default=lambda self: self._get_default_val('use_members_list')
    )
    use_partners_list = fields.Boolean(
        string='Uses partners list',
        default=lambda self: self._get_default_val('use_partners_list')
    )
    auto_production_state = fields.Boolean(
        string="Automatic 'Production state' mode?", 
        default=lambda self: self._get_default_val('auto_production_state'))
    close_to_draft = fields.Boolean(
        string="Can re-open a contract?",
        default=lambda self: self._get_default_val('close_to_draft'))
    use_cn_seq = fields.Boolean(
        string="Use the contract sequences", 
        default=lambda self: self._get_default_val('use_cn_seq'))
    date_format = fields.Char(
        string='Date format', 
        size=15, 
        default=lambda self: self._get_default_val('date_format'))

    # ---------- Instances management

    @api.multi
    def set_values_to_db(self):
        list_fields = [
            'use_members_list',
            'use_partners_list',
            'auto_production_state',
            'close_to_draft',
            'use_cn_seq',
            'date_format'
        ]

        eagle_cfg_param_obj = self.env['eagle.config.params']

        for name_field in list_fields:
            rec = eagle_cfg_param_obj.search([])
            value_field = getattr(self, name_field)
            if rec.exists():
                rec = rec[0]
                rec.write({name_field: value_field})
            else:
                rec.create({name_field: value_field})
