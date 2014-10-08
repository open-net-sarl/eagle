# -*- coding: utf-8 -*-
#
#  File: edoctree.py
#  Module: eagle_edoctree
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

import logging
from osv import fields, osv

class eDocTree_node(osv.osv):
    _inherit = 'ons.edoctree.node'

    _columns = {
        'contract_id': fields.many2one('eagle.contract', 'Contract'),
        'meta_id': fields.many2one('eagle.contract.meta', 'Meta-contract'),
    }
    
    def write(self, cr, uid, ids, vals, context={}):
        if isinstance(ids, (int,long)): ids = [ids]

        child_ids = []
        ctx = context.copy()
        if ('contract_id' in vals or 'meta_id' in vals) and not context.get('edoctree_skip_me', False):
            child_ids = self.search(cr, uid, [('id','child_of',ids)], context=context)
            ctx['edoctree_skip_me'] = True
        
        ret = super(eDocTree_node, self).write(cr, uid, ids, vals, context=ctx)
        
        if child_ids:
            children_vals = {}
            if 'contract_id' in vals:
                children_vals['contract_id'] = vals['contract_id']
            if 'meta_id' in vals:
                children_vals['meta_id'] = vals['meta_id']
            if children_vals:
                self.write(cr, uid, child_ids, children_vals, context=ctx)
        
        return ret

    # ------------ Instances management

    def copy_node(self, cr, uid, source, target, new_name, template=False, skip_root=False, context=None):
        return super(eDocTree_node, self).copy_node(cr, uid, source, target, new_name, template=template, skip_root=skip_root, context=context)
    
    def button_synch_contract_with_edoctree(self, cr, uid, ids, context={}):
        contract_id = context.get('current_contract_id', False)
        if not contract_id: 
            return False
        
        cnt = self.pool.get('eagle.contract').read(cr, uid, contract_id, ['name'], context=context)
        if not cnt or not cnt.get('name', False):
            return False

        vals = {
            'name': cnt['name'],
            'meta_id': context.get('current_meta_id', False),
        }
        return self.pool.get('eagle.contract').update_edoctree_node_ref(cr, uid, [contract_id], vals, context=context)

eDocTree_node()
