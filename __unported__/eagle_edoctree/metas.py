# -*- coding: utf-8 -*-
#
#  File: metas.py
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

import logging
_logger = logging.getLogger(__name__)

class eagle_meta( osv.osv ):
    _inherit = 'eagle.contract.meta'

    def _find_edoctree_children(self, cr, uid, cnt_ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        
        edoctree_obj = self.pool.get('ons.edoctree.node')
        param_obj = self.pool.get('ons_edoctree.config.settings')
        param_ids = param_obj.search(cr, uid, [], context=context)
        parameters = param_ids and param_obj.read(cr, uid, param_ids[len(param_ids)-1], ['nod_type'], context=context)
        container = parameters and parameters.get('nod_type', False)
        
        for cnt_id in cnt_ids:
            filter = [('contract_id','=',cnt_id)]
            if container: filter += [('nod_type','=',container)]
            res[cnt_id] = edoctree_obj.search(cr, uid, filter, context=context)
        
        return res
    
    def check_tabs_profile(self, cr, uid, meta_ids, field_names, args, context={}):
        return self.pool.get('eagle.contract').check_tabs_profile(cr, uid, meta_ids, field_names, args, context=context)

    _columns = {
        'edoctree_ids': fields.one2many('ons.edoctree.node', 'meta_id', 'Nodes'),
        'tab_profile_edoctree_m': fields.function(check_tabs_profile, method=True, type='boolean', string='tab_profile_edoctree_m', multi='tab_profile_edoctree'),
        'edoctree_children': fields.function(_find_edoctree_children, method=True, type='one2many', relation='ons.edoctree.node', string='children'),
    }

eagle_meta()
