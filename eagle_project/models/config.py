# -*- coding: utf-8 -*-
#
#  File: models/config.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class eagle_config_params(models.Model):
    _inherit = 'eagle.config.params'

    # ---------- Fields management

    inv_close_cnt_if_inv_payed = fields.Boolean(string='May close a contract only if all invoices are paid')
    

class eagle_config_settings(models.TransientModel):
    _inherit = 'eagle.config.settings'

    @api.model
    def _get_default_val(self, field_name):
        val = False
        eagle_config_params = self.env['eagle.config.params']
        line = eagle_config_params.search([])
        if line.exists():
            val = getattr(line[0], field_name)
        return val

    # ---------- Fields management

    inv_close_cnt_if_inv_payed = fields.Boolean(
        string='May close a contract only if all invoices are paid',
        default=lambda self: self._get_default_val('inv_close_cnt_if_inv_payed'))

    # ---------- Instances management

    @api.multi
    def set_values_to_db(self):
        res = super(eagle_config_settings, self).set_values_to_db()

        list_fields = [
            'inv_close_cnt_if_inv_payed'
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

