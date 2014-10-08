# -*- coding: utf-8 -*-
#
#  File: sales.py
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

import netsvc
from osv import fields, osv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from tools.translate import _
import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class sale_order( osv.osv ):
    _inherit = 'sale.order'
    
    # ---------- Fields management

    _columns = {
        'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
        # This field is automatically set at the moment when a contract is set to "open"
        # Else, it's always False. Sale order and invoice report will be set accordingly.
        'financial_partner_id': fields.many2one( 'res.partner', 'Funded by' ),
        'sale_partner_id': fields.many2one( 'res.partner', 'Shipping to' ),
    }

    # ---------- Utilities
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        inv = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
        inv.update({
            'contract_id':order.contract_id and order.contract_id.id or False,
            'financial_partner_id':order.financial_partner_id and order.financial_partner_id.id or False,
        })
        
        return inv

    def _prepare_order_picking(self, cr, uid, order, context=None):
        return super(sale_order, self)._prepare_order_picking(cr, uid, order, context=context)
        
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, date_planned, context=None):
        planned_date = date_planned
        if order_line and order_line.contract_pos_id and order_line.contract_pos_id.stock_disposal_date:
            planned_date = order_line.contract_pos_id.stock_disposal_date
        return super(sale_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, planned_date, context=context)

    def _prepare_order_line_procurement(self, cr, uid, order, order_line, move_id, date_planned, context=None):
        planned_date = date_planned
        if order_line and order_line.contract_pos_id:
            planned_date = order_line.contract_pos_id.stock_disposal_date
        ret = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, order_line, move_id, date_planned, context=context)
        if order_line and order_line.contract_id:
            ret['contract_id'] = order_line.contract_id.id
        
        return ret

sale_order()

class sale_order_line( osv.osv ):
    _inherit = 'sale.order.line'
    
    # ---------- Fields management

    _columns = {
        'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
        'contract_pos_id': fields.many2one( 'eagle.contract.position', 'Contract Position' ),
    }

sale_order_line()

class sale_shop( osv.osv ):
    _inherit = 'sale.shop'

    # ---------- Fields management

    def _count_nb_linked_countracts(self, cr, uid, ids, field_name, arg, context={}):
        ret = {}
        for cnt in self.read( cr, uid, ids, ['eagle_contracts'], context=context ):
            ret[cnt['id']] = len(cnt['eagle_contracts'])
        
        return ret
    
    _columns = {
        'eagle_contracts_nb': fields.function( _count_nb_linked_countracts, method=True, type='integer', string='Nb. linked contracts' ),
        'eagle_contracts': fields.one2many( 'eagle.contract', 'shop_id', 'Linked contracts' ),
    }
    
sale_shop()
