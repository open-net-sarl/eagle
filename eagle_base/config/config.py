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

import openerp
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.models import MAGIC_COLUMNS

class eagle_config_params(osv.osv):
    _name = 'eagle.config.params'
    _description = 'Eagle Configuration Parameters'
    
    # ---------- Fields management

    _columns = {
        'name': fields.char('Name', size=40),
        'use_price': fields.boolean('Uses price', help='If True, the contract and its position will display the prices and the amounts.'),
        'use_members_list': fields.boolean('Uses members list', help='If True, the contract will display the list of members'),
        'use_partners_list': fields.boolean('Uses partners list', help='If True, the contract will display the list of partners'),
        'use_partners_roles': fields.boolean('Uses partners roles', help='If True, the contract will display the list of partner roles'),
        'inline_pos_edit': fields.boolean('Inline position edition', help='If True, the contract will let you edit the position in the tree'),
        'show_all_meta_tabs': fields.boolean('Show all meta-tabs?'),
        'auto_production_state': fields.boolean("Automatic 'Production state' mode?"),
        'close_to_draft': fields.boolean("Can re-open a contract?"),
        'use_cn_seq': fields.boolean("Use the contract sequences"),
        'date_format': fields.char('Date format', size=15),
        'pos_onchange_prod_field': fields.many2one('ir.model.fields', 'Product field', domain=[('model','in',['product.product','product.template']),('name', 'ilike', 'description')]),

        'tabs': fields.char('Tabs list', size=250),
        'tabs_profile': fields.many2one('eagle.config.tabs_profile', 'Tabs profile'),

        # TODO
        'use_cust_ref_as_cn': fields.boolean("Use the customer's ref as contract name"),

        'void': fields.char(' ', size=1),
    }
    
    _defaults = {
        'name': lambda *a: 'Eagle Parameters',
        'use_price': lambda *a: True, 
        'use_members_list': lambda *a: False, 
        'use_partners_list': lambda *a: False,
        'use_partners_roles': lambda *a: False,
        'auto_production_state': lambda *a: True, 
        'use_cust_ref_as_cn': lambda *a: False,
        'use_cn_seq': lambda *a: False, 
        'date_format': lambda *a: '%d.%m.%Y',
        'void': lambda *a: ' ',
    }

    # ---------- Instances management

    def copy(self, cr, uid, id, default={}, context={}):
        raise osv.except_osv(_('Forbidden!'), _('Eagle must have one and only one record.'))
    
    def get_instance(self, cr, uid, context={}):
        for params in self.browse(cr, uid, self.search(cr, uid, [], context=context), context=context):
            return params
    
        return False

eagle_config_params()

class eagle_config_settings(osv.osv_memory):
    _name = 'eagle.config.settings'
    _inherit = 'res.config.settings'

    # ---------- Fields management

    _columns = {
        'use_price': fields.boolean('Uses price', help='If True, the contract and its positions will display the prices and the amounts.'),

        'use_members_list': fields.boolean('Uses members list', help='If True, the contract will display the list of members.'),
        'use_partners_list': fields.boolean('Uses partners list', help='If True, the contract will display the list of partners.'),
        'use_partners_roles': fields.boolean('Uses partners roles', help='If True, the contract will display the list of partners roles.'),

        'inline_pos_edit': fields.boolean('Inline position edition', help='If True, the contract will let you edit the position in the tree'),

        'show_all_meta_tabs': fields.boolean('Show all tabs?'),
        'tabs_profile': fields.many2one('eagle.config.tabs_profile', 'Tabs profile'),

        'auto_production_state': fields.boolean("Automatic 'Production state' mode?"),
        'close_to_draft': fields.boolean("Can re-open a contract?"),

        'use_cust_ref_as_cn': fields.boolean("Use the customer's ref as contract name"),
        'use_cn_seq': fields.boolean("Use the contracts sequence"),
        
        'date_format': fields.char('Date format', size=15),

        'pos_onchange_prod_field': fields.many2one('ir.model.fields', 'Product field', domain=[('model','in',['product.product','product.template']),('name', 'ilike', 'description')]),
    }

    _defaults = {
        'use_price': lambda *a: True, 
        'use_members_list': lambda *a: False, 
        'use_partners_list': lambda *a: False,
        'use_partners_roles': lambda *a: False,
        'auto_production_state': lambda *a: True, 
        'use_cust_ref_as_cn': lambda *a: False,
        'use_cn_seq': lambda *a: False,
        'date_format': lambda *a: '%d.%m.%Y',
    }

    # ---------- Instances management
    
    def copy_vals(self, rec):
        ret = {}
        if not rec:
            return ret
        for fname, field in self._columns.iteritems():
            if fname in MAGIC_COLUMNS:
                continue
            if isinstance(field,(fields.related,fields.one2many,fields.many2many,fields.sparse,fields.function,fields.dummy,fields.serialized,fields.property)):
                continue
            if isinstance(field,fields.many2one):
                if rec.get(fname, False):
                    ret[fname] = rec[fname][0]
                continue
            if fname in rec:
                ret[fname] = rec[fname]
        
        return ret

    def default_get(self, cr, uid, fields, context=None):
        eagle_cfg_param_obj = self.pool.get('eagle.config.params')
        ids = eagle_cfg_param_obj.search(cr, uid, [], context=context)
        if not ids:
            return {}
        rec = eagle_cfg_param_obj.read(cr, uid, ids[0], [], context=context)
        if not rec:
            return {}
        
        ret = self.copy_vals(rec)
        if ret.get('date_format', False):
            ret['date_format'] = '%d.%m.%Y'
        return ret

    def execute(self, cr, uid, ids, context=None):
        eagle_cfg_param_obj = self.pool.get('eagle.config.params')

        rec = self.read(cr, uid, ids[0], [], context)
        vals = self.copy_vals(rec)

        rec_ids = eagle_cfg_param_obj.search(cr, uid, [], context=context)
        if not rec_ids:
            vals['name'] = 'Eagle Parameters'
            rec_id = eagle_cfg_param_obj.create(cr, uid, vals, context=context)
        else:
            rec_id = rec_ids[0]
            eagle_cfg_param_obj.write(cr, uid, [rec_id], vals, context=context)

        # force client-side reload (update user menu and current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

eagle_config_settings()
 
