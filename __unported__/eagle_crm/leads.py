# -*- coding: utf-8 -*-
#
#  File: crm_lead.py
#  Module: eagle_crm
#
#  Created by sbe@open-net.ch
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

import logging
_logger = logging.getLogger(__name__)

class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    
    _columns = {
        'contract_id': fields.many2one('eagle.contract', 'Contract'),
        'crm_currency_id': fields.many2one('res.currency', 'Currency'),
    }
    
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        form_view_id = False
        data_obj = self.pool.get('ir.model.data')
        if view_type == 'form' and dict(context or {}).get('ons_lead_from_contract', False):
            form_view_id = data_obj._get_id(cr, user, 'crm', 'crm_case_form_view_leads')
        if view_type == 'form' and dict(context or {}).get('ons_opport_from_contract', False):
            form_view_id = data_obj._get_id(cr, user, 'crm', 'crm_case_form_view_oppor')
        if form_view_id:
            row = data_obj.read(cr, user, form_view_id, ['res_id'], context=context)
            if row and row.get('res_id', False):
                view_id = row['res_id']
        return super(crm_lead,self).fields_view_get(cr, user, view_id, view_type, context, toolbar=toolbar, submenu=submenu)

crm_lead()
