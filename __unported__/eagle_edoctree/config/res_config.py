# -*- coding: utf-8 -*-
#
#  File: config/res_config.py
#  Module: ons_productivity_edoctree
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

from osv import orm, osv, fields
from lxml import etree

import logging
_logger = logging.getLogger(__name__)

class edoctree_config_settings(osv.osv_memory):
    _inherit = 'ons_edoctree.config.settings'

    # ------------ Fields management

    _columns = {
        'eagle_meta_new_what': fields.many2one('ons.edoctree.node', 'What'),
        'eagle_meta_new_where': fields.many2one('ons.edoctree.node', 'Where'),
        'eagle_contract_new_what': fields.many2one('ons.edoctree.node', 'What'),
        'eagle_contract_new_where': fields.selection([('meta','Under its meta-contract'),('tree', 'In the eDocTree')], 'Where'),
        'eagle_contract_new_tree': fields.many2one('ons.edoctree.node', 'Where'),
    }
    
    # ------------ In/Out's

    def get_default_edoctree_values(self, cr, uid, fields, context=None):
        vals = super(edoctree_config_settings, self).get_default_edoctree_values(cr, uid, fields, context=context)
        
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if not eagle_params:
            return False
        
        for param_name in ['_meta_new_what','_meta_new_where','_contract_new_what','_contract_new_tree']:
            val = getattr(eagle_params, 'edoctree' + param_name, False)
            if val:
                vals['eagle' + param_name] = val.id
        vals['eagle_contract_new_where'] = getattr(eagle_params, 'edoctree_contract_new_where', False)

        return vals

    def set_eagle_meta_new_what_recursivity(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params:
            eagle_params.write({'edoctree_meta_new_what': config.eagle_meta_new_what and config.eagle_meta_new_what.id or False})
        
        return True
    
    def set_eagle_meta_new_where_recursivity(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params:
            eagle_params.write({'edoctree_meta_new_where': config.eagle_meta_new_where and config.eagle_meta_new_where.id or False})
        
        return True
    
    def set_eagle_contract_new_what_recursivity(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params:
            eagle_params.write({'edoctree_contract_new_what': config.eagle_contract_new_what and config.eagle_contract_new_what.id or False})
        
        return True
    
    def set_eagle_contract_new_where_recursivity(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params:
            eagle_params.write({'edoctree_contract_new_where': config.eagle_contract_new_where or False})
        
        return True
    
    def set_eagle_contract_new_tree_recursivity(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params:
            eagle_params.write({'edoctree_contract_new_tree': config.eagle_contract_new_tree and config.eagle_contract_new_tree.id or False})
        
        return True
    
edoctree_config_settings()
