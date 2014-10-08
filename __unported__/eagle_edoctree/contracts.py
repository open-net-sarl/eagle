# -*- coding: utf-8 -*-
#
#  File: contracts.py
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

from osv import fields, orm, osv

import logging
_logger = logging.getLogger(__name__)

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'

    # ---------- Fields management

    def _find_edoctree_children(self, cr, uid, cnt_ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        
        edoctree_obj = self.pool.get('ons.edoctree.node')
        param_obj = self.pool.get('ons_edoctree.config.settings')
        param_ids = param_obj.search(cr, uid, [], context=context)
        parameters = param_ids and param_obj.read(cr, uid, param_ids[0], ['nod_type'], context=context)
        container = parameters and parameters.get('nod_type', False)
        
        for cnt_id in cnt_ids:
            filter = [('contract_id','=',cnt_id)]
            if container: filter += [('nod_type','=',container)]
            res[cnt_id] = edoctree_obj.search(cr, uid, filter, context=context)
        
        return res
    
    def check_tabs_profile(self, cr, uid, cnt_ids, field_names, args, context={}):
        return super(eagle_contract, self).check_tabs_profile(cr, uid, cnt_ids, field_names, args, context=context)

    _columns = {
        'edoctree_ids': fields.one2many('ons.edoctree.node', 'contract_id', 'Nodes'),
        'tab_profile_edoctree_c': fields.function(check_tabs_profile, method=True, type='boolean', string='tab_profile_edoctree_c', multi='tab_profile_edoctree'),
        'edoctree_children': fields.function(_find_edoctree_children, method=True, type='one2many', relation='ons.edoctree.node', string='children'),
        'edoctree_root_id': fields.many2one('ons.edoctree.node', 'eDocTree Documents'),
    }

    # ---------- Instances management

    def create(self, cr, uid, vals, context=None):
        new_id = super( eagle_contract, self ).create( cr, uid, vals, context=context )
        self.update_edoctree_node_ref(cr, uid, [new_id], vals, context=context)
        return new_id

    def write(self, cr, uid, cnt_ids, vals, context=None):
        ret = super( eagle_contract, self ).write( cr, uid, cnt_ids, vals, context=context )
        return ret
    
    def update_edoctree_node_ref(self, cr, uid, cnt_ids, cnt_vals, context={}):
        if isinstance(cnt_ids, (int,long)): cnt_ids = [cnt_ids]

        config = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if not config: 
            return False
        if not config.edoctree_contract_new_what or not config.edoctree_contract_new_where:
            return False
        
        count = 0
        edoctree_obj = self.pool.get('ons.edoctree.node')
        meta_obj = self.pool.get('eagle.contract.meta')
        for cnt_id in cnt_ids:
            # Check the contract
            cnt = self.read(cr, uid, cnt_id, ['name','meta_id'], context=context)
            if not cnt:
                continue

            # Check the meta, create it if needed
            dest_node = False
            if cnt.get('meta_id'):
                meta_id = cnt['meta_id'][0]
            else:
                tmp = cnt['name'].split('-')
                if len(tmp) > 1:
                    meta_id = meta_obj.create(cr, uid, {'name':tmp[0]}, context=context)
                else:
                    meta_id = False
            if meta_id:
                meta = meta_obj.browse(cr, uid, meta_id, context=context)
                if meta:
                    dest_node = meta.edoctree_root_id
                    if isinstance(config.edoctree_meta_new_what, orm.browse_record) and isinstance(config.edoctree_meta_new_where, orm.browse_record) and not isinstance(dest_node, orm.browse_record):
                        new_node_id = edoctree_obj.copy_node(cr, uid, config.edoctree_meta_new_what, config.edoctree_meta_new_where, meta.name, template=False, skip_root=False, context=context)
                        if new_node_id:
                            meta.write({'edoctree_root_id':new_node_id}, context=context)
                            dest_node = edoctree_obj.browse(cr, uid, new_node_id, context=context)

            # Check the destination
            if config.edoctree_contract_new_where == 'tree':
                if not config.edoctree_contract_new_tree: return False
                dest_node = config.edoctree_contract_new_tree
            if not dest_node:
                _logger.info("No destination node.")
                continue
    
            new_node_id = edoctree_obj.copy_node(cr, uid, config.edoctree_contract_new_what, dest_node, cnt_vals['name'], template=False, skip_root=False, context=context)
            if new_node_id:
                if self.write(cr, uid, [cnt_id], {'edoctree_root_id': new_node_id}, context=context):
                    count += 1
                nodes = edoctree_obj.search(cr, uid, [('id', 'child_of',new_node_id)], context=context)
                if nodes:
                    edoctree_obj.write(cr, uid, nodes, {'contract_id':cnt_id}, context=context)

        return count > 0

    # ---------- Interface management

    def button_synch_edoctree(self, cr, uid, ids, context={}):
        if not ids:
            ids = context.get('active_id', context.get('current_contract_id', False))
            if ids:
                ids = [ids]
        if ids:
            vals = {
                'name': context.get('current_contract_name', ''),
                'meta_id': context.get('current_meta_id', False),
            }
            if vals['name']:
                self.update_edoctree_node_ref(cr, uid, ids, vals, context=context)
        
        return True

eagle_contract()

class eagle_meta( osv.osv ):
    _inherit = 'eagle.contract.meta'

    # ---------- Fields management

    _columns = {
        'edoctree_root_id': fields.many2one('ons.edoctree.node', 'eDocTree Documents'),
    }

    # ---------- Instances management

    def create(self, cr, uid, vals, context=None):
        new_id = super( eagle_meta, self ).create( cr, uid, vals, context=context )
        self.update_edoctree_node_ref(cr, uid, [new_id], vals, context=context)
        return new_id

    def write(self, cr, uid, meta_ids, vals, context=None):
        ret = super( eagle_meta, self ).write( cr, uid, meta_ids, vals, context=context )
        return ret

    def update_edoctree_node_ref(self, cr, uid, meta_ids, meta_vals, context={}):
        if isinstance(meta_ids, (int,long)): meta_ids = [meta_ids]

        config = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if not config: return False
        if not config.edoctree_meta_new_what or not config.edoctree_meta_new_where: return False
        
        count = 0
        for meta_id in meta_ids:
            dest_node = False
            dest_node_id = meta_vals.get('edoctree_root_id', False)
            if not dest_node_id:
                rec = self.read(cr, uid, meta_id, ['edoctree_root_id'], context=context)
                if rec and rec.get('edoctree_root_id', False):
                    dest_node_id = rec['edoctree_root_id'][0]
            if dest_node_id:
                dest_node = self.pool.get('ons.edoctree.node').browse(cr, uid, dest_node_id, context=context)
            if not dest_node:
                dest_node = config.edoctree_meta_new_where
            if not dest_node:
                continue
    
            new_node_id = self.pool.get('ons.edoctree.node').copy_node(cr, uid, config.edoctree_meta_new_what, dest_node, meta_vals['name'], template=False, context=context)
            if new_node_id:
                if self.write(cr, uid, [meta_id], {'edoctree_root_id': new_node_id}, context=context):
                    count += 1

        return count > 0

eagle_meta()
