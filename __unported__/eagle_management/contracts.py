# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_management
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
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
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import tools
from tools.translate import _
import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'
    _eagle_view_selection_mgt_visible = True

    # ---------- Instances management

    def _register_hook(self, cr):
        """ stuff to do right after the registry is built """
        super(eagle_contract, self)._register_hook(cr)
        _logger.info("Registering Eagle Management's events")
        funcs = [ 
            ('inst','do_contract_mgt_installation'),
            ]
        for func_item in funcs:
            self.register_event_function( cr, 'Eagle Management', func_item[0], func_item[1] )
            
    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            return params

        return False
    
    def _eagle_params( self, cr, uid, ids, field_name, args, context={} ):
        res = {}
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if field_name == 'eagle_make_sale_button_visible':
            for id in ids:
                res[id] = True
            if eagle_param:
                if eagle_param.selling_mode == 'disabled':
                    for id in ids:
                        res[id] = False
                else:
                    cnts = self.read(cr, uid, ids, ['state'], context=context )
                    for cnt in cnts:
                        if cnt['state'] not in ['installation','production']:
                            res[id] = False

        return res

    def write(self, cr, uid, cnt_ids, vals, context=None):
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if eagle_param and hasattr(eagle_param, 'mgt_close_cnt_if_inv_payed') and eagle_param.mgt_close_cnt_if_inv_payed and vals.get('state', '') == 'paid':
            
            if isinstance(cnt_ids,(int,long)): cnt_ids = [cnt_ids]
            cnts = self.read( cr, uid, cnt_ids, ['account_invoices'], context=context )
            # [{'account_invoices': [5, 6, 8, 10, 14, 24],'id': 3}]
            valid = True
            for cnt in cnts:
                todo = []
                lst = cnt.get('current_invoice_lines', [])
                if not lst or not len(lst): continue
                cr.execute("""Select count(i.*) 
from account_invoice i 
where i.state not in ('paid','cancel') 
and i.id in %s""", (tuple(lst),))
                row = cr.fetchone()
                if row and row[0] > 0:
                    valid = False
                    break
            if not valid:
                raise osv.except_osv( _('Error'), _("You can't close contract as long as some invoices are not paid") )

        return super( eagle_contract, self ).write( cr, uid, cnt_ids, vals, context=context )
        
    # ---------- Fields management

    def _is_cdd_button_visible( self, cr, uid, ids, field_name, args, context={} ):
        res = {}
        for id in ids:
            res[id] = False
            cnt = self.browse( cr, uid, id, context=context )
            if not cnt or cnt.state not in ['draft','installation','production']: continue
            for cnt_line in cnt.positions:
                if cnt_line.state == 'open':
                    res[id] = True
                    break

        return res

    def check_tabs_profile(self, cr, uid, cnt_ids, field_names, args, context={}):
        return super(eagle_contract,self).check_tabs_profile(cr, uid, cnt_ids, field_names, args, context=context)

    _columns = {
        'current_sale_order_lines': fields.one2many( 'sale.order.line', 'contract_id', 'Current Sale Order Lines', domain=[('state','=','draft')] ),
        'past_sale_order_lines': fields.one2many( 'sale.order.line', 'contract_id', 'Past Sale Order Lines', domain=[('state','<>','draft')] ),
        'account_invoices': fields.one2many( 'account.invoice', 'contract_id', 'Invoices' ),
        'stock_moves': fields.one2many( 'stock.move', 'contract_id', 'Moves' ),
        'purchase_orders': fields.one2many( 'purchase.order', 'contract_id', string="Purchases" ),
        'stock_pickings_in': fields.one2many( 'stock.picking.in', 'contract_id', 'Incoming products', domain=[('type','=','in')] ),
        'stock_pickings_out': fields.one2many( 'stock.picking.out', 'contract_id', 'Outgoing products', domain=[('type','=','out')] ),
        'procurement_orders': fields.one2many( 'procurement.order', 'contract_id', string="Procurements" ),
        'production_orders': fields.one2many( 'mrp.production', 'contract_id', string="Productions" ),
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, domain="[('company_id','=',company_id)]"),

        'eagle_cdd_button_visible': fields.function( _is_cdd_button_visible, method=True, type='boolean', string="'Set Customer Delivery' Button visible?" ),
        'eagle_make_sale_button_visible': fields.function( _eagle_params, method=True, type='boolean', string="'Make Sale' Button visible?" ),

        'tab_profile_cur_sol': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_cur_sol', multi='tab_profile_cur_sol' ),
        'tab_profile_old_sol': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_old_sol', multi='tab_profile_cur_sol' ),
        'tab_profile_purchases': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_purchases', multi='tab_profile_cur_sol' ),
        'tab_profile_invoices': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_invoices', multi='tab_profile_cur_sol' ),
        'tab_profile_procurements': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_procurements', multi='tab_profile_cur_sol' ),
        'tab_profile_manufacturing': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_moves', multi='tab_profile_cur_sol' ),
        'tab_profile_moves': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_notes', multi='tab_profile_cur_sol' ),
        'tab_profile_incoming_prods': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_incoming_prods', multi='tab_profile_cur_sol' ),
        'tab_profile_outgoing_prods': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_outgoing_prods', multi='tab_profile_cur_sol' ),
    }

    def get_default_shop( self, cr, uid, context ):
        user = self.pool.get( 'res.users' ).browse( cr, uid, uid, context=context )
        shop = self.pool.get( 'sale.shop' ).search( cr, uid, [('company_id','=',user.company_id.id)], context=context, limit=1)
        
        return shop and len(shop) and shop[0] or False
    
    _defaults = {
        'shop_id': get_default_shop,
    }
    
    # ---------- Utilities

    def get_sale_default_values(self, cr, uid, contract, salesman, context={}):
        cr.execute( "select s.id from sale_shop s, stock_warehouse w, res_users u where s.warehouse_id=w.id and w.company_id=u.company_id and u.id=" + str( uid ) )
        row = cr.fetchone()
        if not row or len( row ) < 1:
            if exception_allowed:
                raise osv.except_osv(_('Error !'), _('No Sale Shop found with the current user!\nPlease define one.'))
            _logger.debug( "No Sale Shop found with the current user... please select one" )
            return False
        shop_id = row[0]

        vals = {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'sale.order', context=context),
            'date_order': datetime.now().strftime( '%Y-%m-%d' ),
            'shop_id': shop_id,
            'partner_id': contract.customer_id.id,
            'financial_partner_id': contract.financial_partner_id and contract.financial_partner_id.id or False,
            'user_id': uid,
            'contract_id': contract.id,
            'sale_partner_id': contract.sale_partner_id and contract.sale_partner_id.id or False,
            'fiscal_position': contract.fiscal_position and contract.fiscal_position.id or False,
            'user_id': salesman,
        }

        part = self.pool.get('sale.order').onchange_partner_id(cr, uid, [], contract.customer_id.id)
        vals.update(part['value'])
        if isinstance(vals.get('parent_partner_id', False), tuple):
            vals['parent_partner_id'] = vals['parent_partner_id'][0]

        if contract.pricelist_id:
            vals['pricelist_id'] = contract.pricelist_id.id
        
        return vals

    def get_sale_line_default_values(self, cr, uid, cnt_line, so, context={}):
        fp = so.fiscal_position and so.fiscal_position.id or False
        tmp = self.pool.get('sale.order.line').product_id_change(cr, uid, [], so.pricelist_id.id, cnt_line.name.id, 
                qty=cnt_line.qty, partner_id=so.partner_id.id, date_order=so.date_order, fiscal_position=fp)
        vals = tmp['value']
        vals.update({
            'order_id':  so.id,
            'contract_id':  cnt_line.contract_id.id,
            'salesman_id':  uid,
            'product_id':  int(cnt_line.name),
            'product_uom_qty':  cnt_line.qty,
            'product_uos_qty':  cnt_line.qty,
            'contract_pos_id':  cnt_line.id,
            'price_unit':  cnt_line.list_price,
            'notes':  cnt_line.notes,
            'sequence':  cnt_line.sequence,
            'property_ids':  [(6, 0, [x.id for x in cnt_line.property_ids])],
            'tax_id':  [(6,0, [x.id for x in cnt_line.tax_id])],
            'type': cnt_line.product_type,
        })
        if cnt_line.out_description and cnt_line.out_description != '':
            vals['name'] = cnt_line.out_description
        if not cnt_line.is_billable:
            vals['discount'] = 100.0

        return vals

    # ---------- States management

    def _make_the_sales( self, cr, uid, ids, context={}, handle_financial_partner=False, exception_allowed=False ):
        _logger.debug( "_make_the_sales() called" )

        sales = self.pool.get( 'sale.order' )
        sale_lines = self.pool.get( 'sale.order.line' )
        contracts_lines = self.pool.get( 'eagle.contract.position' )
        recurrences = self.pool.get( 'product.recurrence.unit' )
        projects = self.pool.get( 'project.project' )

        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        use_one_project = eagle_param and eagle_param.use_one_project or False

        if isinstance( ids, (int, long) ):
            ids = [ids]

        for contract in self.browse( cr, uid, ids, context=context ):
            if contract.state not in ['installation','production']:
                continue
            
            salesman = contract.user_id and contract.user_id.id or uid
            
            # Loop through the sale order line and add the products while needed:
            #    - recurrents objects are added if the current date is after the cancellation deadline 
            #        and before the next invoice date
            #    - for non-recurrents objects:
            #        - those in 'open' state are added
            #        - the others are skipped
            #    - each time a contract line is copied into a sale order line, its state is set to 'done'
            #    - if a financial partner is defined, then the non-recurrent products are put in a separated
            #      SO with the financial partner defined
            #      Else:
            #        - non-recurrent products are put in a sale order
            #        - recurrent products may be put either in the same or in a different SO, depending on
            #          how much time has passed between 1st SO and 1st occurence of the recurrent products
            so_id = False
            so = False
            fp = False
            for cnt_line in contract.positions:
                if cnt_line.state != 'open':
                    continue

                now = datetime.now()
                if cnt_line.next_invoice_date:
                    next = datetime.strptime( cnt_line.next_invoice_date, '%Y-%m-%d' )
                    if now < next:
                        continue

                if not cnt_line.cl_start_date:
                    vals = {}
                    cl_start_date = now
                    vals['cl_start_date'] = now.strftime( '%Y-%m-%d' )
                    vals['stock_disposal_date'] = (cl_start_date + relativedelta(days=cnt_line.product_duration)).strftime('%Y-%m-%d')
                    contracts_lines.write( cr, uid, [cnt_line.id], vals, context=context )

                if not so_id:
                    if not handle_financial_partner:
                        so_ids = sales.search( cr, uid, [ ( 'state', '=', 'draft' ), ( 'contract_id', '=', contract.id ) ] )
                        if so_ids and len( so_ids ) > 0:
                            for so in sales.browse( cr, uid, so_ids, context=context ):
                                if so.financial_partner_id:
                                    so_id = so.id
                                    break
                            if not so_id:
                                so_id = so_ids[len(so_ids)-1]
                    if not so_id:
                        ctx = context.copy()
                        ctx.update({'contract_id':contract.id})
                        
                        vals = self.get_sale_default_values(cr, uid, contract, salesman, context=ctx)
                        so_id = sales.create( cr, salesman, vals, context=context )

                        if so_id and hasattr(contract, 'project_id'):
                            if contract.project_id:
                                if use_one_project:
                                    proj_use = 'grouping'
                                else:
                                    proj_use = contract.state == 'installation' and 'inst' or 'maint'
                                proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id),('project_use','=',proj_use)], context=context )
                                if not proj_ids or not len( proj_ids ):
                                    proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id)], context=context )
                                if proj_ids and len( proj_ids ):
                                    proj = projects.browse( cr, uid, proj_ids[0], context=context )
                                    if proj and proj.analytic_account_id:
                                        sales.write( cr, salesman, [so_id], {'project_id':proj.analytic_account_id.id} )
                if not so_id:
                    break
                if not so:
                    so = sales.browse( cr, uid, so_id, context=context )
                    if not so:
                        so_id = False
                        break
                
                now = datetime.now().strftime( '%Y-%m-%d' )
                if not cnt_line.next_invoice_date or cnt_line.next_invoice_date == now:
                    vals = self.get_sale_line_default_values(cr, uid, cnt_line, so, context=context)
                    _logger.debug( "During install, about to create a Sol with vals="+str(vals))
                    sol_id = sale_lines.create( cr, salesman, vals, context=context )

                    if sol_id:
                        contracts_lines.write( cr, salesman, [cnt_line.id], { 'state': 'done' }, context=context )

            if handle_financial_partner:
                so_id = False
                so = False
        
            if contract.state == 'production':

                for cnt_line in contract.positions:
                    if not cnt_line.is_active: continue
                    if cnt_line.state != 'recurrent': continue
                    if not cnt_line.recurrence_id: continue
                    if not cnt_line.next_invoice_date: continue
    
                    recurrence = recurrences.browse( cr, uid, cnt_line.recurrence_id.id )
                    if not recurrence:
                        continue
    
                    now = datetime.now().strftime( '%Y-%m-%d' )
                    next = datetime.strptime( cnt_line.next_invoice_date, '%Y-%m-%d' )
                    dt = next - relativedelta( days=cnt_line.cancellation_deadline )
                    before = dt.strftime( '%Y-%m-%d' )
                    if recurrence.unit == 'day':
                        after = next + relativedelta( days=recurrence.value )
                        if recurrence.value > 0:
                            if not recurrence.keep_same_day:
                                after -= relativedelta( days=1 )
                                s_after = after
                            else:
                                s_after = after - relativedelta( days=1 )
                    elif recurrence.unit == 'month':
                        after = next + relativedelta( months=recurrence.value )
                        if recurrence.value > 0:
                            if not recurrence.keep_same_day:
                                after -= relativedelta( days=1 )
                                s_after = after
                            else:
                                s_after = after - relativedelta( days=1 )
                    elif recurrence.unit == 'year':
                        after = next + relativedelta( years=recurrence.value )
                        if recurrence.value > 0:
                            if not recurrence.keep_same_day:
                                after -= relativedelta( days=1 )
                                s_after = after
                            else:
                                s_after = after - relativedelta( days=1 )
                    if before > now:
                        continue

                    if not cnt_line.cl_start_date:
                        vals = {}
                        cl_start_date = datetime.now()
                        vals['cl_start_date'] = now
                        vals['stock_disposal_date'] = (cl_start_date + relativedelta(days=cnt_line.product_duration)).strftime('%Y-%m-%d')
                        contracts_lines.write( cr, uid, [cnt_line.id], vals, context=context )
                    
                    if not so_id:
                        so_ids = sales.search( cr, uid, [ ( 'state', '=', 'draft' ), ( 'contract_id', '=', contract.id ) ] )
                        if so_ids and len( so_ids ) > 0:
                            for so in sales.browse( cr, uid, so_ids, context=context ):
                                if not so.financial_partner_id:
                                    so_id = so.id
                                    break
                        if not so_id:
                            ctx = context.copy()
                            ctx.update({'contract_id':contract.id})

                            vals = self.get_sale_default_values(cr, uid, contract, salesman, context=ctx)
                            so_id = sales.create(cr, salesman, vals, context=ctx)

                            if so_id and hasattr(contract, 'project_id'):
                                if contract.project_id:
                                    # 2011-01-11/Cyp: Jae asked to put recurrrent tasks in 'Maintenance' project
                                    #proj_use = contract.state == 'installation' and 'inst' or 'maint'
                                    if use_one_project:
                                        proj_use = 'grouping'
                                    else:
                                        proj_use = 'maint'
                                    proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id),('project_use','=',proj_use)], context=context )
                                    if not proj_ids or not len( proj_ids ):
                                        proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id)], context=context )
                                    if proj_ids and len( proj_ids ):
                                        proj = projects.browse( cr, uid, proj_ids[0], context=context )
                                        if proj and proj.analytic_account_id:
                                            sales.write( cr, salesman, [so_id], {'project_id':proj.analytic_account_id.id} )
                            so = False
                        if not so_id:
                            break
                    if so_id and not so:
                        so = sales.browse( cr, uid, so_id, context=context )
                    if not so:
                        so_id = False
                        break

                    vals = self.get_sale_line_default_values(cr, uid, cnt_line, so, context=context)
                    _logger.debug( "During production, about to create a Sol with vals="+str(vals))
                    sol_id = sale_lines.create( cr, salesman, vals, context=context )

                    if sol_id:
                        contracts_lines.write( cr, salesman, [cnt_line.id], { 'next_invoice_date': after.strftime( '%Y-%m-%d' ), 'out_description': txt }, context=context )

            eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
            if eagle_param and eagle_param.auto_production_state:
                valid = True
                for cnt_line in contract.positions:
                    if cnt_line.state == 'open':
                        valid = False
                        break
                if valid:
                    self.contract_production( cr, salesman, [contract.id], {} )

        return True

    # Start the installation
    def do_contract_mgt_installation( self, cr, uid, cnt_ids, context={}, force_sale=False ):
        _logger.debug( "do_contract_mgt_installation() called" )
        
        if isinstance(cnt_ids, (int,long)):
            cnt_ids = [cnt_ids]

        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )        
        if not eagle_param:
            return False
        if eagle_param.selling_mode != 'auto' and not force_sale:
            return False

        for cnt_id in cnt_ids:
            hfp = False
            cnt = self.browse( cr, uid, cnt_id, context=context )
            if cnt and cnt.financial_partner_id:
                hfp = True
            self._make_the_sales( cr, uid, cnt_id, context=context, handle_financial_partner=hfp, exception_allowed=True )

        return True

    # Activate the "Accounting" tabs
    def button_view_moves(self, cr, uid, ids, context={}):
        self.write( cr,uid,ids,{'view_selection':'moves'} )
        return True

    def button_make_sale(self, cr, uid, ids, context={}):
        return self.do_contract_mgt_installation( cr, uid, ids, context=context, force_sale=True )

    # ---------- Scheduler management
    

    def run_mgt_scheduler( self, cr, uid, context={} ):
        ''' Runs Management scheduler.
        '''
        if not context:
            context={}
        
        self_name = 'Eagle Management Scheduler'
        for contract in self.browse( cr, uid, self.search( cr, uid, [], context=context ), context=context ):
            if contract.state in ['installation','production']:
                _logger.debug( "Checking contract '%s'" % contract.name )
                self.do_contract_mgt_installation( cr, uid, [contract.id], context=context )
        
        return True

eagle_contract()

class eagle_contract_pos(osv.osv):
    _inherit = 'eagle.contract.position'

    # ---------- Fields management

    def _comp_start_date(self, cr, uid, pos_ids, field_name, arg, context=None):
        res = {}
        for pos_id in pos_ids:
            res[pos_id] = False
            pos = self.browse( cr, uid, pos_id, context=context)
            if pos and pos.stock_disposal_date:
                ds = datetime.strptime(pos.stock_disposal_date, '%Y-%m-%d')
                res[pos_id] = (ds + relativedelta(days=-pos.product_duration)).strftime('%Y-%m-%d')
        return res

    _columns = {
        'cust_delivery_date': fields.date('Customer Delivery Date'),
        'stock_disposal_date': fields.date('Stock Disposal Date'),
        'product_duration': fields.integer('Duration'),
        'cl_start_date': fields.function( _comp_start_date, method=True, type='date', string='Start date' ),
    }

    _defaults = {
    }

    # ---------- Utilities

    def recomp_start_date(self, cr, uid, ids, disposal_date, duration):
        res = { 'cl_start_date': False }
        if disposal_date:
            ds = datetime.strptime(disposal_date, '%Y-%m-%d')
            res['cl_start_date'] = (ds + relativedelta(days=-duration)).strftime('%Y-%m-%d')
        return { 'value': res }

eagle_contract_pos()
