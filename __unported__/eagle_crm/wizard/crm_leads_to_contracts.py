# -*- coding: utf-8 -*-
#
#  File: wizard/crm_leads_to_contracts.py
#  Module: eagle_crm
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

from openerp.osv import fields, osv
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class crm_leads_to_contracts(osv.osv_memory):
    _name = 'eagle.wiz_crm_leads_to_contracts'
    
    _columns = {
    }

    def do_it(self, cr, uid, ids, context=None):
        context = dict(context or {})
        new_ids = []
        for lead in self.pool.get('crm.lead').browse(cr, uid, context.get('active_ids', []), context=context):
            if lead.contract_id:
                continue
            vals = {
                'name': lead.name,
                'date_start': (lead.date_open or fields.datetime.now()).split(' ')[0],
                'notes': lead.description, 
                'planned_revenue': lead.planned_revenue,
                'probability': lead.probability,
                'crm_currency_id': (lead.crm_currency_id and lead.crm_currency_id.id) or (lead.company_currency and lead.company_currency.id) or False,
            }
            if lead.partner_id:
                vals['partners'] = [(6,0,[lead.partner_id.id])]
            if lead.user_id:
                vals['user_id'] = lead.user_id.id
            if lead.type == 'opportunity':
                vals.update({
                    'state': 'confirm',
                    'src_crm_if_opport': lead.id,
                })
            else:
                vals.update({
                    'state': 'draft',
                    'src_crm_if_lead': lead.id,
                })
            
            new_id = self.pool.get('eagle.contract').create(cr, uid, vals, context=context)
            if new_id:
                lead.write({'contract_id': new_id})
                new_ids.append(new_id)
        
        res = False
        if new_ids:
            data_obj = self.pool.get('ir.model.data')
            form_view_id = data_obj._get_id(cr, uid, 'eagle_base', 'eagle_view_contract_form')
            form_view = data_obj.read(cr, uid, form_view_id, ['res_id'])
            tree_view_id = data_obj._get_id(cr, uid, 'eagle_base', 'eagle_view_contract_tree')
            tree_view = data_obj.read(cr, uid, tree_view_id, ['res_id'])
            search_view_id = data_obj._get_id(cr, uid, 'eagle_base', 'eagle_view_contract_filter')
            search_view = data_obj.read(cr, uid, search_view_id, ['res_id'])
        
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'eagle_base', 'eagle_action_contract_filter_all_tree', context)
            res['domain'] = [('id','in',new_ids)]
                
        return res

crm_leads_to_contracts()
