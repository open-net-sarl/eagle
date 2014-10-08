# -*- coding: utf-8 -*-
#
#  File: partners.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014 Open-Net Ltd. All rights reserved.
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

from osv import osv,fields
from tools.translate import _
from collections import OrderedDict
import re

import logging
_logger = logging.getLogger(__name__)

class eagle_contract_partner_role_type(osv.osv):
    _name = 'eagle.contract.partner_role_type'
    _description = 'Partner role type in an Eagle contract'
    
    _columns = {
        'name': fields.char('Name', size=64, translate=True, required=True),
        'type': fields.selection([
                    ('invoice', 'Invoicing'),
                    ('delivery', 'Delivery'),
                    ('other', 'Other')], 'Type', required=True),
    }

eagle_contract_partner_role_type()

class eagle_contract_partner_role(osv.osv):
    _name = 'eagle.contract.partner_role'
    _description = 'Partner role in an Eagle contract'
    
    _columns = {
        'name': fields.many2one('eagle.contract.partner_role_type', 'Role type', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'contract_id': fields.many2one('eagle.contract', 'Contract', required=True)
    }

eagle_contract_partner_role()

class res_partner(osv.osv):
    _inherit = 'res.partner'

    # ---------- Eagle management

    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            return params

        return False
    
    def _eagle_params( self, cr, uid, part_ids, field_name, args, context={} ):
        res = {}
        val = False
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
                
        if field_name == 'eagle_parm_use_partners_roles':
            val = True
            if eagle_param:
                val = eagle_param.use_partners_roles
                
        if not part_ids:
            res = val
        else:
            for part_id in part_ids:
                res[part_id] = val

        return res
        
    def check_tabs_profile(self, cr, uid, part_ids, field_names, args, context={}):

        tabs_profile = False
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if current_user.eagle_tabs_profile:
            tabs_profile = current_user.eagle_tabs_profile
        if not tabs_profile:
            eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
            if eagle_param.tabs_profile:
                tabs_profile = eagle_param.tabs_profile
        fields_lst = {}
        if not tabs_profile:
            for fld in field_names:
                fields_lst[fld] = False
        else:
            profiles = re.sub(r'[^;^a-z_]+','',str(tabs_profile.opts)).split(';')
            _logger.debug("Profiles options are:"+str(profiles))
            _logger.debug("field names are:"+str(field_names))
            for fld in field_names:
                fields_lst[fld] = False
                tab_name = fld[18:]     # remove 'eagle_tab_profile_' and keep the end
                if tab_name in profiles:
                    fields_lst[fld] = True

        res = {}
        for part_id in part_ids:
            res[part_id] = fields_lst

        return res

    # ---------- Field management

    def _eagle_contract_list(self, cr, uid, part_ids, field_names, args, context=None):
        ret = {}
        for partner in self.browse(cr, uid, part_ids, context=context):
            ref_partner = partner.parent_id or partner
            p_list = [p.id for p in ref_partner.child_ids]
            
            items = self.pool.get('eagle.contract').search(cr, uid, ['|',('partners', 'in', p_list),('customer_id', 'in', p_list)], context=context)
            res = list(OrderedDict.fromkeys(items))
            ret[partner.id] = {
                'eagle_contract_list': res,
                'eagle_contract_count': len(res),
            }
        
        return ret

    def _comp_name(self, cr, uid, ids, name, args, context=None):
        return dict(self.name_get(cr, uid, ids, context=context))

    _columns = {
        'contract_roles_id': fields.one2many('eagle.contract.partner_role', 'partner_id', 'Roles'),
        'eagle_contracts': fields.many2many('eagle.contract', 'eagle_contract_partner_rel', 'partner_id', 'contract_id', 'Present in contracts'),
        'comp_name': fields.function(_comp_name, type='char', string='Name', store=False),
        'eagle_contract_list': fields.function(_eagle_contract_list, type='one2many', relation='eagle.contract', string='Contract list', store=False, multi='eagle_contract_list'),
        'eagle_contract_count': fields.function(_eagle_contract_list, type='integer', string='Contracts count', store=False, multi='eagle_contract_list'),

        'eagle_parm_use_partners_roles': fields.function( _eagle_params, method=True, type='boolean', string="Uses partners roles list?" ),
        'eagle_tab_profile_part_roles': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_partners_roles', multi='eagle_tab_profile_part_roles'),
        'eagle_tab_profile_part_contracts_list': fields.function( check_tabs_profile, method=True, type='boolean', string='eagle_tab_profile_part_contracts_list', multi='eagle_tab_profile_part_roles'),
    }

res_partner()

class eagle_contract(osv.osv):
    _inherit = 'eagle.contract'
    
    _columns = {
        'partner_roles_id': fields.one2many('eagle.contract.partner_role', 'contract_id', 'Partners roles'),
    }

eagle_contract()
