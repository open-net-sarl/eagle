# -*- coding: utf-8 -*-
#
#  File: config/models/config.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class eagle_config_params(models.Model):
    _inherit = 'eagle.config.params'

    # ---------- Fields management

    inv_close_cnt_if_inv_payed = fields.Boolean(string='May close a contract only if all invoices are paid')
    

class eagle_config_settings(models.Model):
    _inherit = 'eagle.config.settings'

    # ---------- Fields management

    inv_close_cnt_if_inv_payed = fields.Boolean(string='May close a contract only if all invoices are paid')

