# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_rebuild_pos_seq.py
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
