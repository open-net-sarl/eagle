# -*- coding: utf-8 -*-
#
#  File: config/config.py
#  Module: eagle_base
#  Eagle's config management
#
#  Created by cyp@open-net.ch
#
#   Starting with the version 5.0, Eagle's parameters are not any more managed
#   using the old, classic way, but rather through OE V7 configuration management:
#   Each time the settings are saved, Eagle's parameters are stored.
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class eagle_config_params( osv.osv ):
    _inherit = 'eagle.config.params'
    
    # ---------- Fields management

    _columns = {
        'edoctree_meta_new_what': fields.many2one('ons.edoctree.node', 'What'),
        'edoctree_meta_new_where': fields.many2one('ons.edoctree.node', 'Where'),
        'edoctree_contract_new_what': fields.many2one('ons.edoctree.node', 'What'),
        'edoctree_contract_new_where': fields.selection([('meta','Under its meta-contract'),('tree', 'In the eDocTree')], 'Where'),
        'edoctree_contract_new_tree': fields.many2one('ons.edoctree.node', 'Where'),
    }

    def get_instance( self, cr, uid, context={} ):
        return super(eagle_config_params, self).get_instance(cr, uid, context=context)
    
eagle_config_params()

