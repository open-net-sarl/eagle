# -*- coding: utf-8 -*-
#
#  File: models/base.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import time
from odoo import models

import logging
_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    def get_next_char(self, number_next):
        val = super(IrSequence, self).get_next_char(number_next)
        if '(eagle_contract)' in val:
            contract_name = ''
            contract_id = context.get('contract_id', False)
            if contract_id:
                contract = self.env['eagle.contract'].read(self._cr, self._uid, [contract_id], ['name'])
                if contract and contract[0].get('name'):
                    contract_name = contract[0]['name']
            val = val.replace('(eagle_contract)', contract_name)

        return val