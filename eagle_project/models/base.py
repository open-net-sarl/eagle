# -*- coding: utf-8 -*-
#
#  File: models/base.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2012-TODAY Open-Net Ltd. <http://www.open-net.ch>

import time

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def _next(self):
        return super(IrSequence, self)._next()

