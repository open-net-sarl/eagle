# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_copy_positions_to.py
#  Module: eagle_invoice
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014 Open-Net Ltd. All rights reserved.
##############################################################################
#
# Author Yvon Philippe Crittin / Open Net Sarl
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import time

class wiz_copy_positions_to(osv.osv_memory):
    _name = 'eagle.wiz_copy_positions_to'
    _description = 'Eagle wizard: copy the positions to another contract'
    
    # ---------- Fields management

    _columns = {
        'src_id': fields.many2one('eagle.contract', 'Copy', required=True),
        'dst_id': fields.many2one('eagle.contract', 'To', required=True),
    }
    
    _defaults = {
        'src_id': lambda s,c,u,ct: ct.get('active_id', False),
    }

    def do_it(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        
        pos_obj = self.pool.get('eagle.contract.position')
        
        datas = self.browse(cr, uid, ids[0], context=context)
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
            new_pos_id = pos_obj.copy(cr, uid, pos.id, defaults, context=context)

        return {}

wiz_copy_positions_to()
