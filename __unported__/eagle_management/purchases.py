# -*- coding: utf-8 -*-
#
#  File: purchases.py
#  Module: eagle_contracts
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2010 Open-Net Ltd. All rights reserved.
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

from osv import fields, osv
import netsvc

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    # ---------- Fields management

    _columns = {
        'contract_id': fields.many2one('eagle.contract', 'Contract'),
    }
    
    # ---------- Workflow related

    def _prepare_order_picking(self, cr, uid, order, context=None):
        ret = super(purchase_order, self)._prepare_order_picking(cr, uid, order, context=context)
        if order.contract_id:
            ret['contract_id'] = order.contract_id.id
        
        return ret

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        ret = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context)
        if order.contract_id:
            ret['contract_id'] = order.contract_id.id
        
        return ret

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        ret = super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
        
        return ret

purchase_order()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    def action_confirm(self, cr, uid, ids, context=None):
        for pol in self.browse(cr, uid, ids, context=context):
            if pol.order_id and pol.order_id.contract_id and pol.order_id.contract_id.project_id:
                pol.write({'account_analytic_id': pol.order_id.contract_id.project_id.analytic_account_id.id})
        
        return super(purchase_order_line, self).action_confirm(cr, uid, ids, context=context)

purchase_order_line()

