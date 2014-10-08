# -*- coding: utf-8 -*-
#
#  File: wizard/crm_make_sale.py
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

class crm_make_sale(osv.osv_memory):
    _inherit = 'crm.make.sale'
    
    _columns = {
        'link_to_eagle': fields.selection([
                            ('no', 'No'),
                            ('yes_new', 'Yes: a new one'),
                            ('yes_exist', 'Yes: an existing one')], 'Link to an Eagle contract', required=True),
        'contract_id': fields.many2one('eagle.contract', 'Contract'),
    }

    def makeOrder(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        ctx = context.copy()
        data = ctx.get('active_ids', [])

        result = super(crm_make_sale, self).makeOrder(cr, uid, ids, context=context)
        # Returns either:
        #     {'type': 'ir.actions.act_window_close'}
        # Or:
        #     {
        #         'domain': str([('id', 'in', new_ids)]),
        #         'view_type': 'form',
        #         'view_mode': 'form',
        #         'res_model': 'sale.order',
        #         'view_id': False,
        #         'type': 'ir.actions.act_window',
        #         'name' : _('Quotation'),
        #         'res_id': new_ids and new_ids[0]
        #     }
        # Or:
        #     {
        #         'domain': str([('id', 'in', new_ids)]),
        #         'view_type': 'form',
        #         'view_mode': 'tree,form',
        #         'res_model': 'sale.order',
        #         'view_id': False,
        #         'type': 'ir.actions.act_window',
        #         'name' : _('Quotation'),
        #         'res_id': new_ids
        #     }
        #
        domain = eval(result.get('domain', 'False'))
        if not domain: return result
        so_ids = domain[0][2]
        
        cnt_vals = []
        case_obj = self.pool.get('crm.lead')
        for so in self.pool.get('sale.order').browse(cr, uid, so_ids, context=ctx):
            for make in self.browse(cr, uid, ids, context=context):
                if make.link_to_eagle == 'no':
                    continue
    
                if make.link_to_eagle == 'yes_exist':
                    if data and make.contract_id:
                        case_obj.write(cr, uid, data, {'contract_id': make.contract_id.id}, context=ctx)
                        if make.contract_id.project_id:
                            so.write({
                                'project_id':make.contract_id.project_id.analytic_account_id.id,
                                'contract_id': make.contract_id.id
                            }, context=ctx)
                    continue
                
                for case in case_obj.browse(cr, uid, data, context=context):
                    vals = {
                        'name': case.name,
                        'customer_id': so.partner_id.id
                    }
                    cnt_id = contract_obj.create(cr, uid, vals, context=ctx)
                    if not cnt_id:
                        continue

                    case_obj.write(cr, uid, data, {'contract_id': cnt_id}, context=ctx)
                    contract_obj._setup_the_projects(cr, uid, [cnt_id], context=ctx)
                    cnt = contract_obj.browse(cr, uid, cnt_id, context=ctx)
                    if not cnt:
                        continue

                    so.write({
                        'project_id':cnt.project_id.analytic_account_id.id,
                        'contract_id': cnt_id
                    }, context=ctx)
        
        return result

crm_make_sale()
