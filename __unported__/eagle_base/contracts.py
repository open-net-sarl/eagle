# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_base
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

from osv import osv,fields
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import tools
from tools.translate import _
import decimal_precision as dp
from openerp.osv.orm import MAGIC_COLUMNS
from openerp import SUPERUSER_ID
from lxml import etree
import re

import logging
_logger = logging.getLogger(__name__)

class eagle_contract_category( osv.osv ):
    _name = 'eagle.contract.category'
    _description = 'Contract category'
    
    _columns = {
        'name': fields.char( 'Category', size=64 ),
    }

eagle_contract_category()

class eagle_contract_base( osv.osv ):
    _name = 'eagle.contract'
    _description = 'Eagle contract'
    _inherit = ['mail.thread']

    # ---------- Fields management

    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            return params

        return False
    
    def _eagle_params( self, cr, uid, pos_ids, field_name, args, context={} ):
        res = {}
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if field_name == 'eagle_parm_auto_production_state':
            val = True
            if eagle_param:
                val = eagle_param.auto_production_state
                
            for pos_id in pos_ids:
                res[pos_id] = val

        return res
        
    _columns = {
        'name': fields.char( 'Contract', type='char', size=64, required=True ),
    }

    # ---------- Instances management
        
    def _register_hook(self, cr):
        """ stuff to do right after the registry is built """
        _logger.info("Registering Eagle Base's events")
        funcs = [ 
            ('draft','do_contract_base_draft'),
            ('inst','do_contract_base_installation'),
            ('conf','do_contract_base_confirmation'),
            ('prod','do_contract_base_production'),
            ('closed','do_contract_base_close'),
            ('canceled','do_contract_base_cancel') ]
        for func_item in funcs:
            self.register_event_function( cr, 'Eagle Base', func_item[0], func_item[1] )

    def register_event_function( self, cr, module_descr, cfg_event_name, function_name ):
        uid = SUPERUSER_ID
        if 'eagle.config.event' not in self.pool.obj_list():
            return False

        do_commit = False
        cfg_events = self.pool.get('eagle.config.event')
        cfg_event_ids = cfg_events.search( cr, uid, [('name','=',cfg_event_name)] )
        if cfg_event_ids and len(cfg_event_ids):
            cfg_event_id = cfg_event_ids[0]
        else:
            cfg_event_id = cfg_events.create( cr, uid, {'name':cfg_event_name} )
            do_commit = True
        if not cfg_event_id:
            return False
        found = False
        cfg_event = cfg_events.browse( cr, uid, cfg_event_id )
        if not cfg_event: return False
        for line in cfg_event.lines:
            if line.function_name == function_name:
                found = True
                break
        if not found:
            vals = {
                'name': cfg_event_id,
                'function_name': function_name,
                'seq': len(cfg_event.lines),
                'module_descr': module_descr,
            }
            self.pool.get( 'eagle.config.event.line' ).create( cr, uid, vals )
            do_commit = True
        
        if do_commit:
            cr.commit()

        return True

    def unregister_event_function( self, cr, cfg_event_name, function_name ):
        uid = 1
        if 'eagle.config.event' not in self.pool.obj_list():
            return False

        cfg_events = self.pool.get('eagle.config.event')
        cfg_event_ids = cfg_events.search( cr, uid, [('name','=',cfg_event_name)] )
        if cfg_event_ids and len(cfg_event_ids):
            cfg_event_id = cfg_event_ids[0]
        else:
            return False
        if not cfg_event_id: return False
        
        cfg_event_lines = self.pool.get('eagle.config.event.line')
        line_ids = cfg_event_lines.search(cr, uid, [('name','=',cfg_event_id),('function_name','=',function_name)])
        if line_ids:
            self.pool.get( 'eagle.config.event.line' ).unlink( cr, uid, line_ids )

        return True

    # ---------- States management

    # Start the installation
    def do_contract_base_installation( self, cr, uid, ids, context={} ):
        self.write( cr,uid,ids,{'state':'installation'}, context=context )
        return True

    # Start the production
    def do_contract_base_production( self, cr, uid, ids, context={} ):
        self.write( cr,uid,ids,{'state':'production'}, context=context )
        return True

    # Close the contract
    def do_contract_base_close( self, cr, uid, ids, context={} ):
        self.write( cr,uid,ids,{'state':'closed'}, context=context )
        return True

    # Cancel the contract
    def do_contract_base_cancel( self, cr, uid, ids, context={} ):
        self.write( cr,uid,ids,{'state':'canceled'}, context=context )
        return True

    # Start an offer
    def do_contract_base_draft( self, cr, uid, ids, context={} ):
        self.write( cr,uid,ids,{'state':'draft'}, context=context )
        return True

    # Confirm the contract
    def do_contract_base_confirmation( self, cr, uid, ids, context={} ):
        self.write( cr,uid,ids,{'state':'confirm'}, context=context )
        return True

    # Generic function, used to react to all Eagle Config based events
    def handle_event( self, cr, uid, ids, cfg_event_name, context={} ):
        ret = True
        cfg_events = self.pool.get('eagle.config.event')
        cfg_event_ids = cfg_events.search( cr, uid, [('name','=',cfg_event_name)], context=context )
        if cfg_event_ids and len(cfg_event_ids):
            cfg_event = cfg_events.browse( cr, uid, cfg_event_ids[0], context=context )
            if cfg_event:
                for cfg_event_line in cfg_event.lines:
                    # Determine if self has at least a member with a name stored in the event config. line
                    if not hasattr(self,cfg_event_line.function_name): continue
                    # Determine if the newly detected member is a function or not
                    func = getattr(self,cfg_event_line.function_name)
                    if not hasattr(func,'__call__'): continue
                    #  Yes, call it!!
                    if func(cr, uid, ids, context):
                        ret = True
        
        return ret
        
    # This handles the automatic state changes, if active in Eagle's parameters
    def check_state( self, cr, uid, contract_ids, context={} ):
        if isinstance( contract_ids, (int,long) ): contract_ids = [contract_ids]

        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if not eagle_param or not eagle_param.auto_production_state or len(contract_ids) < 1:
            return False

        ret = False

        # As of vers. 4.7.01+, a contract in "Installation" state with no position to install
        # and if it's set in Eagle's configuration, is automatically change to "Production"
        to_do = []
        for cnt in self.browse( cr, uid, contract_ids, context=context ):
            if cnt.state != 'installation': continue
            add_it = True
            for pos in cnt.positions:
                if pos.state == 'open':
                    add_it = False
                    break
            if add_it:
                to_do.append(cnt.id)
        if len(to_do)> 0:
            ret = self.handle_event( cr, uid, to_do, 'prod', context )
        
        return ret

    # Response to the "Set to Draft" button
    def contract_draft( self, cr, uid, ids, context ):
        return self.handle_event( cr, uid, ids, 'draft', context={} )

    # Response to the "Set to Confirm" button
    def contract_confirm( self, cr, uid, ids, context ):
        return self.handle_event( cr, uid, ids, 'conf', context={} )

    # Response to the "Set to Installation State" button
    def contract_installation( self, cr, uid, ids, context={} ):
        if isinstance(ids, (int,long)): ids = [ids]
        for row in self.read(cr, uid, ids, ['customer_id'], context=context):
            if not row.get('customer_id', []):
                raise osv.except_osv(_('Error !'), _('Please select a customer.'))
        ret = self.handle_event( cr, uid, ids, 'inst', context )
        self.check_state( cr, uid, ids, context=context )
        
        return ret

    # Response to the "Set to Production State" button
    def contract_production( self, cr, uid, ids, context={} ):
        if isinstance(ids, (int,long)): ids = [ids]
        for row in self.read(cr, uid, ids, ['customer_id'], context=context):
            if not row.get('customer_id', []):
                raise osv.except_osv(_('Error !'), _('Please select a customer.'))
        return self.handle_event( cr, uid, ids, 'prod', context )

    # Response to the "Set to Closed State" button
    def contract_close( self, cr, uid, ids, context={} ):
        return self.handle_event( cr, uid, ids, 'closed', context )

    # Response to the "Set to Closed State" button
    def contract_cancel( self, cr, uid, ids, context={} ):
        return self.handle_event( cr, uid, ids, 'canceled', context )

eagle_contract_base()

class eagle_contract_pos(osv.osv):
    _name = 'eagle.contract.position'
    _description = 'Contract position'
    _order = 'sequence,id'
    
    # ---------- Fields management

    def _amount_line_base(self, cr, uid, line_ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        
        for line in self.browse(cr, uid, line_ids, context=context):
            if line.is_billable and field_name == 'cl_total':
                price = line.list_price
                if line.discount:
                    price *= (100 - line.discount) / 100.0
                res[line.id] = price * line.qty
            else:
                res[line.id] = 0.0
        
        return res

    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            return params

        return False
    
    def _eagle_params( self, cr, uid, pos_ids, field_name, args, context={} ):
        res = {}
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if field_name == 'eagle_parm_use_price':
            val = True
            if eagle_param:
                val = eagle_param.use_price
                
            if not pos_ids:
                res = val
            else:
                for pos_id in pos_ids:
                    res[pos_id] = val

        return res

    def _get_is_invoicable( self, cr, uid, pos_ids, name, args, context ):
        res = {}
        dt_today = datetime.today().strftime('%Y-%m-%d')
        _logger.debug( 'addons.'+self._name + ": Is Invoicable: now: %s" % str(dt_today) )
        for pos in self.browse( cr, uid, pos_ids, context=context ):
            res[pos.id] = False
            if pos.state == 'done': continue
            _logger.debug( 'addons.'+self._name+"    ---- Date: %s  status: %s" % ( str(pos.next_invoice_date), str(pos.state) ) )
            res[pos.id] = True
        
        return res

    _columns = {
        'name': fields.many2one( 'product.product', 'Product', required=True ),
        'qty': fields.float( 'Quantity' ),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure'),
        'contract_id': fields.many2one( 'eagle.contract', 'Contract', required=True ),
        'recurrence_id': fields.many2one( 'product.recurrence.unit', 'Recurrence' ),
        'next_invoice_date': fields.date( 'Next action date' ),
        'state': fields.selection( [
                ( 'open','To install' ),
                ( 'done','Installed' ),
                ( 'recurrent','Recurrent' ),
                ( 'progressive','Progressive' ),
                ], 'State' ),
        'cancellation_deadline': fields.integer( 'Days before' ),
        'is_active': fields.boolean( 'Active' ),
        'is_billable': fields.boolean( 'Billable?' ),
        'start_of_period': fields.boolean( 'Start of period?' ),
        'sequence': fields.integer('Sequence'),
        'description': fields.char( 'Description', type='char', size=250 ),
        'out_description': fields.char('Reported text', size=256),
        'list_price': fields.float('Sale Price', digits_compute=dp.get_precision('Sale Price'), help="Base price for computing the customer price."),
        'cl_total': fields.function( _amount_line_base, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
        'discount': fields.float('Discount'),
        'notes': fields.text( 'Notes', translate=True ),
        'property_ids': fields.many2many('mrp.property', 'position_property_rel', 'contract_id', 'property_id', 'Properties'),
        'progr_rate': fields.float('Rate [%]'),
        'progr_invoiced': fields.boolean('Invoiced'),
        #                                   , fnct_search=_search_is_invoicable
        'is_invoicable': fields.function( _get_is_invoicable, method=True, type='boolean', string="Is invoicable?", store=True ),

        'eagle_parm_use_price': fields.function( _eagle_params, method=True, type='boolean', string="Uses prices?" ),
        'product_type': fields.selection([('make_to_stock', 'from stock'), ('make_to_order', 'on order')], 'Procurement Method', required=True,
                        help="From stock: When needed, the product is taken from the stock or we wait for replenishment.\nOn order: When needed, the product is purchased or produced."),
    }

    _defaults = {
        'state': 'open',
        'sequence': 1,
        'is_billable': lambda *a:True,
        'out_description': lambda *a:'',
        'eagle_parm_use_price': lambda s,cr,uid,c: s._eagle_params(cr, uid, False, 'eagle_parm_use_price', False, context=c),
        'product_type': 'make_to_stock',
    }

    # ---------- Utilities

    def recomp_line(self, cr, uid, ids, product, customer, qty, list_price, discount):
        if not product or not customer: return False

        price = list_price
        if discount:
            price *= (100 - discount) / 100.0
        return { 'value': {
            'cl_total': qty * price,
        } }

    def recomp_line_sw(self, cr, uid, ids, contract_id, product, qty, list_price, discount):
        if not product or not customer: return False

        contract = self.pool.get('eagle.contract').read(cr, uid, contract_id, ['customer_id'])
        customer_id = contract and contract.get('customer_id', False) or False
        if customer_id: customer_id = customer_id[0]
        
        return self.recomp_line(cr, uid, ids, product, customer_id, qty, list_price, discount)

    # ---------- Interface related

    def onchange_description(self, cr, uid, ids, description, recurrence_id, next_invoice_date, start_of_period, context={}):
        txt = tools.ustr(description or '')
        if not next_invoice_date or not recurrence_id:
            return {
            'value': { 'out_description': txt or '' }
        }
        if 'lang' not in context:
            context = { 'lang': self.pool.get('res.users').browse(cr,uid,uid).lang }
        start_date = datetime.strptime( next_invoice_date, '%Y-%m-%d' )
        end_date = start_date
        recurrence = self.pool.get( 'product.recurrence.unit' ).browse( cr, uid, recurrence_id, context=context )
        if recurrence:
            if start_of_period:
                if recurrence.unit == 'day':
                    start_date -= relativedelta( days=recurrence.value )
                elif recurrence.unit == 'month':
                    start_date -= relativedelta( months=recurrence.value )
                elif recurrence.unit == 'year':
                    start_date -= relativedelta( years=recurrence.value )
            if recurrence.unit == 'day':
                end_date = start_date + relativedelta( days=recurrence.value )
            elif recurrence.unit == 'month':
                end_date = start_date + relativedelta( months=recurrence.value )
            elif recurrence.unit == 'year':
                end_date = start_date + relativedelta( years=recurrence.value )
            if recurrence.value > 0:
                end_date -= relativedelta( days=1 )

            if txt:
                if txt != '': txt += ' - '
            else:
                txt = ''
            
            eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
            date_format = eagle_param.date_format or '%d.%m.%Y'
            txt += start_date.strftime( date_format ) + ' ' + _( 'to' ) + ' ' + end_date.strftime( date_format )
        
        return {
            'value': { 'out_description': txt or '' }
        }

    def onchange_recurrence(self, cr, uid, ids, recurrence_id, context={}):
        res = { 'qty': 1 }
        if not recurrence_id:
            res['state'] = 'open'
            res['cancellation_deadline'] = False
            res['next_invoice_date'] = False
        else:
            if 'lang' not in context:
                context = { 'lang': self.pool.get( 'res.users' ).browse( cr, uid, uid ).lang }
            recurrence = self.pool.get( 'product.recurrence.unit' ).browse( cr, uid, recurrence_id, context=context )
            if recurrence:
                now = datetime.now().strftime( '%Y-%m-%d' )
                if recurrence.unit == 'day':
                    next = datetime.strptime( now, '%Y-%m-%d' ) + relativedelta( days=recurrence.value )
                    if recurrence.value > 0:
                        next -= relativedelta( days=1 )
                    res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
                    res['state'] = 'recurrent'
                    res['cancellation_deadline'] = 30
                    res['is_active'] = True
                elif recurrence.unit == 'month':
                    next = datetime.strptime( now, '%Y-%m-%d' ) + relativedelta( months=recurrence.value )
                    if recurrence.value > 0:
                        next -= relativedelta( days=1 )
                    res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
                    res['state'] = 'recurrent'
                    res['cancellation_deadline'] = 30
                    res['is_active'] = True
                elif recurrence.unit == 'year':
                    next = datetime.strptime( now, '%Y-%m-%d' ) + relativedelta( years=recurrence.value )
                    if recurrence.value > 0:
                        next -= relativedelta( days=1 )
                    res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
                    res['state'] = 'recurrent'
                    res['cancellation_deadline'] = 30
                    res['is_active'] = True
        
        return {
            'value': res
        }
        
    def onchange_product(self, cr, uid, ids, product_id, qty, date_start, partner_id, pricelist_id, start_of_period):
        res = {}
        if not product_id:
            _logger.debug( 'addons.'+self._name+": Eagle Base's onchange_product() is returning nothing because there's no product id" )
            return { 'value': {} }
        
        usr = self.pool.get('res.users').browse(cr, uid, uid)
        customer = partner_id and self.pool.get( 'res.partner' ).browse( cr, uid, partner_id ) or False
        context = {'lang':usr.lang}
        if customer:
            context['lang'] = customer.lang
        if partner_id:
            context['partner_id'] = partner_id
        
        prod = self.pool.get( 'product.product' ).browse( cr, uid, product_id, context=context )
        if not prod:
            raise osv.except_osv(_('Error !'), _('Product not found.'))
            
        res['description'] = prod.name
        res['notes'] = prod.description_sale
        res['uom_id'] = prod.uom_id and prod.uom_id.id or False
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params and eagle_params.pos_onchange_prod_field:
            tmp = getattr(prod, eagle_params.pos_onchange_prod_field.name, False)
            if tmp:
                res['notes'] = tmp

        if not qty or qty == 0.0:
            qty = 1.0
            res['qty'] = qty

        res['product_type'] = 'make_to_stock'
        if prod.type == 'product':
            if prod.supply_method == 'buy':
                delay = prod.sale_delay
                if prod.seller_ids and len(prod.seller_ids) > 0:
                    suppl = prod.seller_ids[0]
                    delay = suppl.delay
            else:    # prod.supply_method == 'produce'
                delay = prod.produce_delay
            res['product_type'] = prod.procure_method
        elif prod.type == 'service':
            uom = prod.uom_id
            q = 1.0
            if uom and uom.factor_inv != 0.0:
                q = uom.factor_inv
            delay = qty * q
        else:
            delay = prod.sale_delay or False

        # 2011-06-28/Cyp/Jae moved to Eagle Management
        #res['product_duration'] = delay
        res['list_price'] = prod.list_price

        next = False
        if not prod.recurrence_id:
            res['state'] = 'open'
            res['recurrence_id'] = False
            res['cancellation_deadline'] = 0
            res['next_invoice_date'] = False
            res['is_active'] = False
        else:
            res['state'] = 'recurrent'
            res['recurrence_id'] = prod.recurrence_id.id
            res['cancellation_deadline'] = 30
            res['is_active'] = True
            if not date_start:
                if prod.recurrence_id.unit == 'day':
                    d = datetime.now().strftime( '%Y-%m-%d' )
                    date_start = datetime.strptime(d, '%Y-%m-%d' ) + relativedelta( days=1 )
                else:
                    d = datetime.now().strftime( '%Y-%m-1' )
                    date_start = datetime.strptime(d, '%Y-%m-%d') + relativedelta( months=1 )
                date_start = date_start.strftime('%Y-%m-%d')
                
            res['next_invoice_date'] = date_start
            next = False
            if prod.recurrence_id.unit == 'day':
                next = datetime.strptime(date_start, '%Y-%m-%d' ) + relativedelta( days=prod.recurrence_id.value ) 
            elif prod.recurrence_id.unit == 'month':
                next = datetime.strptime(date_start, '%Y-%m-%d' ) + relativedelta( months=prod.recurrence_id.value )
            elif prod.recurrence_id.unit == 'year':
                next = datetime.strptime(date_start, '%Y-%m-%d' ) + relativedelta( years=prod.recurrence_id.value )
            if next:
                if prod.recurrence_id.value > 0:
                    next -= relativedelta( days=1 )
                res['next_invoice_date'] = next.strftime( '%Y-%m-%d' )
            
        if pricelist_id and partner_id:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
                        prod.id, qty or 1.0, partner_id, {
                            'uom': prod.uom_id.id,
                            'date': date_start,
                            })[pricelist_id]
            if price:
                res.update({'list_price': price})
        res.update( { 'cl_total': qty * res['list_price'] } )

        vals = self.onchange_description( cr, uid, ids, res['description'], res['recurrence_id'], res['next_invoice_date'], start_of_period, context=context )
        res.update( vals['value'] )

        _logger.debug( 'addons.'+self._name+": Eagle Base's onchange_product() is returning: %s",str(res) )
        return { 'value': res }

    def onchange_product_sw(self, cr, uid, ids, contract_id, product_id, qty, start_of_period):
        res = {}
        if not product_id or not contract_id:
            _logger.debug( 'addons.'+self._name+": Eagle Base's onchange_product() is returning nothing because there's no product id" )
            return { 'value': {} }
        contract = self.pool.get('eagle.contract').read(cr, uid, contract_id, ['date_start', 'customer_id', 'pricelist_id'])
        if not contract:
            return { 'value': {} }
        date_start = contract.get('date_start', False)
        customer_id = contract.get('customer_id', False)
        if customer_id: customer_id = customer_id[0]
        pricelist_id = contract.get('pricelist_id', False)
        if pricelist_id: pricelist_id = pricelist_id[0]
        
        return self.onchange_product(cr, uid, ids, product_id, qty, date_start, customer_id, pricelist_id, start_of_period)

    def onchange_progr_rate(self, cr, uid, ids):
        return { 'value': { 'progr_invoiced': False } }
        
    def button_disable(self, cr, uid, ids, context={}):
        self.write( cr,uid,ids,{'is_active':False} )
        return True

    def button_enable(self, cr, uid, ids, context={}):
        self.write( cr,uid,ids,{'is_active':True} )
        return True

    def create(self, cr, uid, vals, context=None):
        return super( eagle_contract_pos, self ).create( cr, uid, vals, context=context )

    def write(self, cr, uid, pos_ids, vals, context=None):
        ret = super( eagle_contract_pos, self ).write( cr, uid, pos_ids, vals, context=context )
        return ret

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        context = context or {}
        res = super(eagle_contract_pos, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if view_type in ['tree']:
            eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
            use_price = True
            if eagle_param:
                use_price = eagle_param.use_price
                eview = etree.fromstring(res['arch'])
                field = False
                if not use_price:
                    field = eview.xpath("//field[@name='cl_total']")
                    if field:
                        field[0].set('invisible','1')
                        field[0].set('modifiers', field[0].get('modifiers').replace('false', 'true'))
                if context.get('ons_switchable_edition', False):
                    param = eagle_param.inline_pos_edit
                    usr = self.pool.get('res.users').browse(cr, uid, uid, context=context)
                    if usr.eagle_parm_inline_pos_edit == 'no':
                        param = False
                    elif usr.eagle_parm_inline_pos_edit == 'yes':
                        param = True
                    if param:
                        field = eview.xpath("//tree")
                        if field:
                            field[0].set('editable','bottom')
                if field:
                    res['arch'] = etree.tostring(eview)

        return res

eagle_contract_pos()

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'

    # ---------- Eagle management
    
    def read_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.read( cr, uid, params_obj.search( cr, uid, [], context=context ), [], context=context ):
            return params
        
        return []
    
    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            return params

        return False
    
    def _eagle_params( self, cr, uid, cnt_ids, field_name, args, context={} ):
        res = {}
        val = False
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )

        if field_name == 'eagle_parm_use_price':
            val = True
            if eagle_param:
                val = eagle_param.use_price
                
        if field_name == 'eagle_parm_use_members_list':
            val = True
            if eagle_param:
                val = eagle_param.use_members_list
                
        if field_name == 'eagle_parm_use_partners_list':
            val = True
            if eagle_param:
                val = eagle_param.use_partners_list
                
        if field_name == 'eagle_parm_use_partners_roles':
            val = True
            if eagle_param:
                val = eagle_param.use_partners_roles
                
        if field_name == 'eagle_parm_use_req_list':
            val = True
            if eagle_param:
                val = eagle_param.use_req_list
                
        if field_name == 'eagle_parm_show_all_meta_tabs':
            val = False
            if eagle_param:
                val = eagle_param.show_all_meta_tabs
                
        if field_name == 'eagle_parm_auto_production_state':
            val = True
            if eagle_param:
                val = eagle_param.auto_production_state
                
        if field_name == 'eagle_parm_inline_pos_edit':
            val = True
            if eagle_param:
                val = eagle_param.inline_pos_edit
            usr = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            if usr.eagle_parm_inline_pos_edit == 'no':
                val = False
            elif usr.eagle_parm_inline_pos_edit == 'yes':
                val = True
                
        if not cnt_ids:
            res = val
        else:
            for cnt_id in cnt_ids:
                res[cnt_id] = val

        return res
        
    def check_tabs_profile(self, cr, uid, cnt_ids, field_names, args, context={}):

        tabs_profile = False
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if current_user.eagle_tabs_profile:
            tabs_profile = current_user.eagle_tabs_profile
        if not tabs_profile:
            eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
            if eagle_param.tabs_profile:
                tabs_profile = eagle_param.tabs_profile
        if not tabs_profile:
            raise osv.except_osv( _('Invalid configuration!'), 
                    _("Please define a tab's profile in Eagle's configuration!") )
        profiles = re.sub(r'[^;^a-z_]+','',str(tabs_profile.opts)).split(';')
        _logger.debug("Profiles options are:"+str(profiles))
        _logger.debug("field names are:"+str(field_names))
        fields_lst = {}
        for fld in field_names:
            fields_lst[fld] = False
            tab_name = fld[12:]     # remove 'tab_profile_' and keep the end
            if tab_name in profiles:
                fields_lst[fld] = True

        res = {}
        for cnt_id in cnt_ids:
            res[cnt_id] = fields_lst

        return res

    # ---------- Fields management

    def _get_cl_total_base( self, cr, uid, cnt_ids, name, args, context={} ):
        res = {}
        for cnt in self.browse( cr, uid, cnt_ids, context=context ):
            tot = 0.0
            for cl in cnt.positions:
                tot += cl.cl_total
            res[cnt.id] = tot
        
        return res
    
    def _get_default_name(self, cr, uid, context={}):
        new_name = _('No name')
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if eagle_param and eagle_param.use_cn_seq:
            obj_sequence = self.pool.get('ir.sequence')
            new_name = obj_sequence.next_by_code(cr, uid, 'eagle.contract', context=context)
        
        return new_name

    def _get_partners_lists(self, cr, uid, cnt_ids, field_name, args, context={}):
        ret = {}
        for cnt in self.browse(cr, uid, cnt_ids, context=context):
            lst_cnt = ["<li> - %s</li>" % x.comp_name for x in cnt.partners]
            ret[cnt.id] = '\n'.join(lst_cnt)
        
        return ret

    _columns = {
        'date_start': fields.date( 'Start date', required=True ),
        'date_end': fields.date( 'End date' ),
        'state': fields.selection( [
                ( 'draft','Offer' ),
                ( 'confirm','Confirmation' ),
                ( 'installation','Installation' ),
                ( 'production','Production' ),
                ( 'closed','Closed' ),
                ( 'canceled','Canceled' ),
                ], 'Contract State' ),
        'customer_id': fields.many2one('res.partner', 'Customer', required=False),
        'user_id': fields.many2one( 'res.users', 'Salesman', readonly=True ),
        'positions': fields.one2many( 'eagle.contract.position', 'contract_id', 'Positions' ),
        'financial_partner_id': fields.many2one( 'res.partner', 'Funded by' ),
        'members': fields.many2many('res.users', 'eagle_contract_user_rel', 'contract_id', 'uid', 'Contract members'),
        'partners': fields.many2many('res.partner', 'eagle_contract_partner_rel', 'contract_id', 'partner_id', 'Contract partners'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist' ),
        'c_total': fields.function( _get_cl_total_base, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
        'company_id': fields.many2one( 'res.company', 'Company', required=True ),
        'notes': fields.text( 'Notes', translate=True ),
        'category_id': fields.many2one( 'eagle.contract.category', 'Category' ),
        'sale_partner_id': fields.many2one( 'res.partner', 'Shipping to' ),
        'cnt_partners': fields.function(_get_partners_lists, method=True, type='char', readonly=True, string='CNT Partners', store=False),
        #'request_ids': fields.one2many('res.request', 'contract_id', 'Requests'),

        'eagle_parm_use_members_list': fields.function( _eagle_params, method=True, type='boolean', string="Uses members list?" ),
        'eagle_parm_show_all_meta_tabs': fields.function( _eagle_params, method=True, type='boolean', string="Show all meta-tabs?" ),
        'eagle_parm_use_price': fields.function( _eagle_params, method=True, type='boolean', string="Uses prices?" ),
        'eagle_parm_use_partners_list': fields.function( _eagle_params, method=True, type='boolean', string="Uses partners list?" ),
        'eagle_parm_use_partners_roles': fields.function( _eagle_params, method=True, type='boolean', string="Uses partners roles list?" ),
        'eagle_parm_inline_pos_edit': fields.function( _eagle_params, method=True, type='boolean', string="Inline position edition?" ),
        #'eagle_parm_use_req_list': fields.function( _eagle_params, method=True, type='boolean', string="Uses requests list?" ),
        
        'tab_profile_positions': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_positions', multi='tab_profile_positions' ),
        #'tab_profile_messages': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_messages', multi='tab_profile_positions' ),
        #'tab_profile_requests': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_requests', multi='tab_profile_positions' ),
        'tab_profile_other_infos': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_other_infos', multi='tab_profile_positions' ),
        'tab_profile_members': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_members', multi='tab_profile_positions' ),
        'tab_profile_partners': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_partners', multi='tab_profile_positions' ),
        'tab_profile_part_roles': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_partners_roles', multi='tab_profile_positions' ),
        'tab_profile_notes': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_notes', multi='tab_profile_positions' ),
        'tab_profile_debug': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_debug', multi='tab_profile_positions' ),
    }

    _defaults = {
        'state': lambda *a:'draft',
        'user_id': lambda self,cr,uid,context: uid,
        'date_start': datetime.now().strftime( '%Y-%m-%d' ),
        'name': _get_default_name,
        'eagle_parm_use_price': lambda s,cr,uid,c: s._eagle_params( cr, uid, False, 'eagle_parm_use_price', False, context=c ),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'res.partner', context=c),
    }
    
    _order = 'date_start desc, id desc'

    # ---------- Instances management

    def create(self, cr, uid, vals, context=None):
        ret_id = super( eagle_contract, self ).create( cr, uid, vals, context=context )
        return ret_id

    def write(self, cr, uid, cnt_ids, vals, context=None):
        if isinstance(cnt_ids, (int,long)): cnt_ids = [cnt_ids]
        for row in self.read(cr, uid, cnt_ids, ['state','customer_id'], context=context):
            if row['state'] not in ['installation', 'production']:
                continue
            if not row.get('customer_id', []):
                if not vals.get('customer_id', False):
                    raise osv.except_osv(_('Error !'), _('Please select a customer.'))

        ret = super( eagle_contract, self ).write( cr, uid, cnt_ids, vals, context=context )
        return ret

    def unlink(self, cr, uid, ids, context=None):
        contracts = self.read(cr, uid, ids, ['state','positions'], context=context)
        unlink_parent_ids = []
        unlink_children_ids = []
        for c in contracts:
            if c['state'] in ['draft']:
                unlink_parent_ids.append(c['id'])
                if len( c['positions'] ) > 0:
                    unlink_children_ids += c['positions']
            else:
                raise osv.except_osv( _('Invalid action !'), 
                    _('Cannot delete contract(s) which are already confirmed !') )
        if len( unlink_children_ids ) > 0:
            self.pool.get( 'eagle.contract.position' ).unlink( cr, uid, unlink_children_ids, context=context )
        return osv.osv.unlink( self, cr, uid, unlink_parent_ids, context=context )

    def copy(self, cr, uid, id, default={}, context={}):
        # !!!!!!!!!!!!!!!!!!
        # The default COPY function tries to copy everything, including one2many stuff
        # which may be completely weird for contract's leads because it tries to copy
        # the addresses as well
        # Solution: create a new record with some of the original's values

        contract = self.browse( cr, uid, id, context=context )
        contract_positions = self.pool.get( 'eagle.contract.position' )

        context_wo_lang = context.copy()
        if 'lang' in context:
            del context_wo_lang['lang']
        data = self.read(cr, uid, [id,], context=context_wo_lang)
        if data:
            data = data[0]
        else:
            raise IndexError( _("Record #%d of %s not found, cannot copy!") %( id, self._name))
        
        blacklist = MAGIC_COLUMNS + ['parent_left', 'parent_right']
        for f, colinfo in self._all_columns.items():
            field = colinfo.column
            if f in blacklist:
                del data[f]
                pass
            elif isinstance(field, fields.function):
                del data[f]
                pass
            elif field._type == 'many2one':
                if field.required:
                    try:
                        data[f] = data[f] and data[f][0]
                    except:
                        pass
                else:
                    data[f] = False
            elif field._type == 'one2many':
                data[f] = []
            elif field._type == 'many2many':
                data[f] = [(6,0,[])]

        data['name'] = contract.name+ _(' (copy)')
        data['state'] = 'draft'

        # Recopy some MANY2ONE attributes
        for attr in ['customer_id','financial_partner_id','pricelist_id','user_id']:
            if not hasattr( contract, attr ): continue
            value = getattr( contract, attr )
            data[attr] = value and value.id or False

        # Recopy some MANY2MANY attributes
        for attr in ['members']:
            if not hasattr( contract, attr ): continue
            values = getattr( contract, attr )
            if values:
                data[attr] = [(6,0,[ x.id for x in values ])]

        _logger.debug("Contract copy: data[]=%s",str(data))
        new_contract_id = self.create( cr, uid, data, context=context ) 

        # Let's copy the contract positions
        for pos in contract.positions:
            vals = {
                'contract_id': new_contract_id, 
                'state': pos.state == 'recurrent' and 'recurrent' or 'open'
            }
            new_pos_id = contract_positions.copy( cr, uid, pos.id, vals, context=context )
            
        return new_contract_id

    # ---------- Interface related

    # Activate the "Contract" tabs
    def button_view_contract(self, cr, uid, ids, context={}):
        return True

    # Activate the "Accounting" tabs
    def button_view_accounting(self, cr, uid, ids, context={}):
        return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(eagle_contract, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if view_type != 'form': return res
        if eagle_param and hasattr(eagle_param,'close_to_draft') and eagle_param.close_to_draft:
            eview = etree.fromstring(res['arch'])
            draft_btn = eview.xpath("//button[@name='contract_draft']")
            if draft_btn:
                draft_btn[0].set('states','confirm,closed,canceled')
                draft_btn[0].set('modifiers','{"invisible": [["state", "not in", ["confirm", "closed", "canceled"]]]}')
                res['arch'] = etree.tostring(eview)
        return res

    def onchange_customer(self, cr, uid, ids, customer_id):
        res = { }
        if customer_id:
            cust = self.pool.get( 'res.partner' ).read( cr, uid, customer_id, ['property_product_pricelist', 'ons_hrtif_to_invoice'] )
            if cust:
                if cust.get('property_product_pricelist', False):
                    res['pricelist_id'] = cust['property_product_pricelist'][0]
                if cust.get('ons_hrtif_to_invoice', False):
                    res['ons_hrtif_to_invoice'] = cust['ons_hrtif_to_invoice'][0]
        return {
            'value': res
        }

    def button_cyp_debug(self, cr, uid, ids, context={}):
        _logger.debug("Cyp:debug called: val=%s",str(val))
        return True

    def action_view_positions(self, cr, uid, cnt_ids, context=None):
        '''
        This function returns an action that display existing positions of given eagle contract ids. It can either be a in a list or in a form view, if there is only one eagle contract to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'eagle_base', 'eagle_action_contract_pos_filter_sw_tree')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        ctx = eval(result.get('context', {}))
        #choose the view_mode according to the number of contracts
        if isinstance(cnt_ids, (int,long)):
            result['domain'] = "[('contract_id','=',"+str(contract_id)+")]"
            ctx['default_contract_id'] = contract_id
        else:
            result['domain'] = "[('contract_id','in',["+','.join(map(str, cnt_ids))+"])]"
            ctx['default_contract_id'] = cnt_ids and cnt_ids[0] or False
        result['context'] = str(ctx)
        
        return result

    # ---------- States management

    def check_contract_items( self, cr, uid, ids, context={} ):
        if isinstance(ids, (int,long)): ids = [ids]

        return True

    # Response to the "Set to Installation State" button
    def contract_installation( self, cr, uid, ids, context={} ):
        self.check_contract_items( cr, uid, ids, context=context )
        return super( eagle_contract, self ).contract_installation( cr, uid, ids, context=context )

    # Response to the "Set to Production State" button
    def contract_production( self, cr, uid, ids, context={} ):
        self.check_contract_items( cr, uid, ids, context=context )
        return super( eagle_contract, self ).contract_production( cr, uid, ids, context=context )

eagle_contract()

class eagle_customer( osv.osv ):
    _name = 'eagle.customer'
    _description = 'Contracts Customers'
    _auto = False
    _rec_name = 'customer'

    # ---------- Fields management

    _columns = {
        'customer': fields.char( 'Customer', size=128, readonly=True),
        'nb_contracts': fields.integer( 'Contracts Nb', readonly=True),
        'void': fields.char('Void', size=1, readonly=True)
    }
    _order = 'customer'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'eagle_customer')
        cr.execute( 'CREATE OR REPLACE VIEW eagle_customer AS (' \
                'SELECT DISTINCT ' \
                "customer_id AS id, res_partner.name as customer, count(eagle_contract.id) as nb_contracts, ' ' as void " \
                'FROM eagle_contract, res_partner ' \
                'where customer_id=res_partner.id ' \
                'group by res_partner.name, customer_id ' \
                'order by res_partner.name )' )

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):

        def child_of_domain(left, ids, left_model, parent=None, prefix='', context=None):
            """ Return a domain implementing the child_of operator for [(left,child_of,ids)],
                either as a range using the parent_left/right tree lookup fields
                (when available), or as an expanded [(left,in,child_ids)] """
            if left_model._parent_store and (not left_model.pool._init):
                # TODO: Improve where joins are implemented for many with '.', replace by:
                # doms += ['&',(prefix+'.parent_left','<',o.parent_right),(prefix+'.parent_left','>=',o.parent_left)]
                doms = []
                for o in left_model.browse(cr, uid, ids, context=context):
                    if doms:
                        doms.insert(0, OR_OPERATOR)
                    doms += [AND_OPERATOR, ('parent_left', '<', o.parent_right), ('parent_left', '>=', o.parent_left)]
                if prefix:
                    return [(left, 'in', left_model.search(cr, uid, doms, context=context))]
                return doms
            else:
                def recursive_children(ids, model, parent_field):
                    if not ids:
                        return []
                    ids2 = model.search(cr, uid, [(parent_field, 'in', ids)], context=context)
                    return ids + recursive_children(ids2, model, parent_field)
                return [(left, 'in', recursive_children(ids, left_model, parent or left_model._parent_name))]

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        dom = child_of_domain('id', [user.company_id.id], self.pool.get('res.company'), context=context)
        
        filter = not dom and '(-1)' or "(%s)" % ','.join([str(x) for x in dom[0][2]])

        cr.execute("select distinct customer_id from eagle_contract where company_id is null or company_id in " + filter)
        
        filter = [('id','in', [x[0] for x in cr.fetchall()])]
        return super(eagle_customer, self).search(cr, uid, filter, offset=offset, limit=limit, order=order, context=context, count=count)

eagle_customer()
