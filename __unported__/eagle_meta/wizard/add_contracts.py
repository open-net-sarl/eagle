# -*- coding: utf-8 -*-
#
#  File: add_contracts.py
#  Module: eagle_meta
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2013 Open-Net Ltd. All rights reserved.
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from tools.translate import _
from osv import osv, fields
import time

class wiz_add_cnt_2_meta_base(osv.osv_memory):

    _name = 'eagle.wiz_add_cnt_2_meta'
    _description = "Eagle wizard: add contracts to meta"

    # ------------ Fields management

    _columns = {
        'meta_id': fields.many2one('eagle.contract.meta', 'Meta-contract', required=True),
    }
    
    _defaults = {
        'meta_id': lambda s, c, u, ctx: ctx.get('active_id', False),
    }

wiz_add_cnt_2_meta_base()

class wiz_add_cnt_2_meta_line(osv.osv_memory):

    _name = 'eagle.wiz_add_cnt_2_meta.line'
    _description = "Eagle wizard: add contracts to meta (line)"

    # ------------ Fields management

    _columns = {
        'wiz_id': fields.many2one('eagle.wiz_add_cnt_2_meta', 'Wizard'),
        'contract_id': fields.many2one('eagle.contract', 'Contract', required=True),
    }
    
wiz_add_cnt_2_meta_line()

class wiz_add_cnt_2_meta(osv.osv_memory):

    _inherit = 'eagle.wiz_add_cnt_2_meta'
    
    # ------------ Fields management

    _columns = {
        'wiz_line_ids': fields.one2many('eagle.wiz_add_cnt_2_meta.line', 'wiz_id', 'Lines'),
    }

    # ------------ User interface related

    def do_it(self, cr, uid, ids, context=None):
        datas = self.browse(cr, uid, ids[0], context=context)
        
        cnt_ids = [l.contract_id.id for l in datas.wiz_line_ids]
        if cnt_ids:
            self.pool.get('eagle.contract').write(cr, uid, cnt_ids, {'meta_id': context['active_id']}, context=context)

        return {}

wiz_add_cnt_2_meta()
