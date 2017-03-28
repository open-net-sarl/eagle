# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_copy_positions_to.py
#  Module: eagle_invoice
#
#  Created by cyp@open-net.ch
#  Updated by lfr@open-net.ch (2017)
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>
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

import logging
_logger = logging.getLogger(__name__)

import time

import odoo
from odoo import fields, models
from odoo.tools.translate import _

class wiz_copy_positions_to(models.TransientModel):
    _name = 'eagle.wiz_copy_positions_to'
    _description = 'Eagle wizard: copy the positions to another contract'
    
    # ---------- Fields management

    src_id = fields.Many2one(
        comodel_name='eagle.contract', 
        string='Copy',
        required=True, 
        default=lambda s,c,u,ct: ct.get('active_id', False)),
    dst_id = fields.Many2one(
        comodel_name='eagle.contract', 
        string='To', 
        required=True),
    

    def do_it(self):
        if not context:
            context = {}
        
        pos_obj = self.env['eagle.contract.position']
        
        datas = self.browse(ids[0])
        if not datas.src_id or not datas.dst_id: return {}
        seq = 0
        for pos in datas.dst_id.positions:
            if seq < pos.sequence:
                seq = pos.sequence 
        for pos in datas.src_id.positions:
            seq += 10
            defaults = {
                'contract_id':datas.dst_id.id, 
                'sequence':seq
            }
            if pos.state == 'done':
                defaults['state'] = 'open'
            new_pos_id = pos_obj.copy(pos.id, defaults)

        return {}

wiz_copy_positions_to()
