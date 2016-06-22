# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_rebuild_pos_seq.py
#  Module: eagle_invoice
#
#  Created by cyp@open-net.ch
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

import openerp
from openerp.osv import osv, fields
from openerp.tools.translate import _

class wiz_rebuild_pos_seq(osv.osv_memory):
    _name = 'eagle.wiz_rebuild_pos_seq'
    _description = 'Eagle wizard: rebuild the sequence of the positions'
    
    # ---------- Fields management

    _columns = {
        'cnt_id': fields.many2one('eagle.contract', 'Contract', required=True),
        'step': fields.integer('Step', required=True),
    }
    
    _defaults = {
        'cnt_id': lambda s,c,u,ct: ct.get('active_id', False),
        'step': lambda *a: 10,
    }

    def do_it(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        
        datas = self.browse(cr, uid, ids[0], context=context)
        if not datas.cnt_id: return {}
        seq = 0
        for pos in datas.cnt_id.positions:
            seq += datas.step
            pos.write({'sequence': seq}, context=context)

        return {}

wiz_rebuild_pos_seq()
