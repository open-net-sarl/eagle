# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_invoice
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
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from tools.translate import _
import tools

import logging
_logger = logging.getLogger(__name__)

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'
    __logger = logging.getLogger('eagle_invoice_contracts')

    # ---------- Instances management

    def _register_hook(self, cr):
        """ stuff to do right after the registry is built """
        super(eagle_contract, self)._register_hook(cr)
        _logger.info("Registering Eagle Invoice's events")
        self.register_event_function( cr, 'Eagle Finances', 'inst', 'do_contract_inv_installation' )

    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            return params

        return False
    
    def _eagle_params( self, cr, uid, cnt_ids, field_name, args, context={} ):
        res = {}
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if field_name == 'eagle_make_invoice_button_visible':
            for cnt_id in cnt_ids:
                res[cnt_id] = True
            if eagle_param:
                if eagle_param.invoicing_mode == 'disabled':
                    for cnt_id in cnt_ids:
                        res[cnt_id] = False
                else:
                    cnts = self.read(cr, uid, cnt_ids, ['state'], context=context )
                    for cnt in cnts:
                        if cnt['state'] not in ['installation','production']:
                            res[cnt_id] = False
                
        return res

    def write(self, cr, uid, cnt_ids, vals, context=None):
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if eagle_param and eagle_param.inv_close_cnt_if_inv_payed and vals.get('state', '') == 'closed':

            todo = {}
            if 'past_invoice_lines' in vals:
                todo['past_invoice_lines'] = vals['past_invoice_lines']
                del vals['past_invoice_lines']
            if 'current_invoice_lines' in vals:
                todo['past_invoice_lines'] = vals['current_invoice_lines']
                del vals['current_invoice_lines']
            if len(todo) > 0:
                ret = super( eagle_contract, self ).write( cr, uid, cnt_ids, todo, context=context )

            if isinstance(cnt_ids,(int,long)): cnt_ids = [cnt_ids]
            cnts = self.read( cr, uid, cnt_ids, ['current_invoice_lines','past_invoice_lines'], context=context )
            # [{'current_invoice_lines': [5, 6, 8, 10, 14, 24],'id': 3,'past_invoice_lines': []}]
            valid = True
            for cnt in cnts:
                todo = []
                lst = cnt.get('current_invoice_lines', [])
                if lst and len(lst): todo += lst
                lst = cnt.get('past_invoice_lines',[])
                if lst and len(lst): todo += lst
                if len(todo):
                    cr.execute("""Select count(i.*) 
from account_invoice i, account_invoice_line l 
where l.invoice_id=i.id 
and i.state not in ('paid','cancel') 
and l.id in %s""", (tuple(todo),))
                    row = cr.fetchone()
                    if row and row[0] > 0:
                        valid = False
                        break
            if not valid:
                raise osv.except_osv( _('Error'), _("You can't close contract as long as some invoices are not paid") )

        return super( eagle_contract, self ).write( cr, uid, cnt_ids, vals, context=context )

    # ---------- Fields management

    def check_tabs_profile(self, cr, uid, cnt_ids, field_names, args, context={}):
        return super(eagle_contract,self).check_tabs_profile(cr, uid, cnt_ids, field_names, args, context=context)

    _columns = {
        'current_invoice_lines': fields.one2many( 'account.invoice.line', 'contract_id', 'Current invoice lines', domain=[('invoice_id.state','=','draft')] ),
        'past_invoice_lines': fields.one2many( 'account.invoice.line', 'contract_id', 'Past invoice lines', domain=[('invoice_id.state','<>','draft')] ),
        'eagle_make_invoice_button_visible': fields.function( _eagle_params, method=True, type='boolean', string="'Make Invoice' Button visible?" ),

        'tab_profile_curr_inv_lines': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_curr_inv_lines', multi='tab_profile_curr_inv_lines' ),
        'tab_profile_past_inv_lines': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_past_inv_lines', multi='tab_profile_curr_inv_lines' ),
    }
    
    # ---------- States management

    def get_invoice_default_values( self, cr, uid, contract, context={} ):
        invoice_obj = self.pool.get( 'account.invoice' )
        journal_obj = self.pool.get('account.journal')
        vals = {
            'name': contract.name,
            'origin': contract.name,
            'type': 'out_invoice',
            'state':'draft',
            'date_invoice': datetime.now().strftime( '%Y-%m-%d' ),
            'partner_id': contract.customer_id and contract.customer_id.id or False,
            'contract_id': contract.id,
            'fiscal_position': contract.fiscal_position and contract.fiscal_position.id or False,
        }
        
        res = journal_obj.search( cr, uid, [('type', '=', 'sale'), ('company_id', '=', contract.company_id.id)], context=context, limit=1 )
        journal_id = res and res[0] or False
        res = invoice_obj.onchange_journal_id( cr, uid, [], journal_id=journal_id )
        if res and res.get('value', False):
            vals['currency_id'] = res['value']['currency_id']
        vals['journal_id'] = journal_id
        
        res = invoice_obj.onchange_partner_id(cr, uid, [], 'out_invoice', vals['partner_id'],\
            date_invoice=vals['date_invoice'], company_id=contract.company_id.id)
        vals.update( res['value'] )
        
        return vals
    
    def get_invoice_line_default_values( self, cr, uid, invoice, contract, contract_position, context={} ):
        invoice_lines = self.pool.get( 'account.invoice.line' )
        product_id = int( contract_position.name )
        product = self.pool.get( 'product.product' ).browse( cr, uid, product_id, context=context )
        vals = {
            'name': contract.name,
            'origin': contract.name,
            'invoice_id': invoice.id,
            'product_id': product_id,
            'contract_id': contract.id,
        }

        res = invoice_lines.product_id_change(cr, uid, [], product.id, product.uom_id and product.uom_id.id or False,  
            qty=contract_position.qty, name=product.name, type='out_invoice', 
            partner_id=contract.customer_id and contract.customer_id.id or False,
            currency_id=invoice.currency_id, context=context)
        vals.update( res['value'] )

        vals.update( {'name': contract_position.out_description} )

        if 'invoice_line_tax_id' in vals:
            vals['invoice_line_tax_id'] = [(6, 0, vals['invoice_line_tax_id'])]

        if contract_position:
            vals.update( {'price_unit': contract_position.list_price,'quantity':contract_position.qty,'invoice_line_tax_id':[(6, 0, [tx.id for tx in contract_position.tax_id])]} )
            if not contract_position.is_billable:
                vals.update( {'discount':100.0} )
        
        return vals

    def do_contract_inv_installation( self, cr, uid, ids, context={}, force_invoicing=False ):
        invoices = self.pool.get( 'account.invoice' )
        invoice_lines = self.pool.get( 'account.invoice.line' )
        recurrences = self.pool.get( 'product.recurrence.unit' )
        contract_positions = self.pool.get( 'eagle.contract.position' )
        projects = self.pool.get( 'project.project' )
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        use_one_project = eagle_param and eagle_param.use_one_project or False
        
        if isinstance(ids, (int,long)):
            ids = [ids]
        
        if not eagle_param:
            return False
        if eagle_param.invoicing_mode != 'auto' and not force_invoicing:
            return False

        for contract in self.browse( cr, uid, ids, context=context ):
            if contract.state not in ['installation','production']:
                continue
            
            salesman = contract.user_id and contract.user_id.id or uid
            
            # This loop handles non-recurrent, non-progressive contract positions 
            #    - those in 'open' state are added
            #    - the others are skipped
            #    - each time an object is correctly added to an invoice, its state is set to 'done'
            invoice_id = False
            invoice = False
            for contract_position in contract.positions:
                if contract_position.state != 'open': continue
                
                # If needed, prepare a new invoice, if not already defined
                if not invoice_id:
                    invoice_ids = invoices.search( cr, uid, [ ('type','=','out_invoice'),('state', '=', 'draft'), ('contract_id', '=', contract.id) ], context=context )
                    if invoice_ids and len(invoice_ids): invoice_id = invoice_ids[0]
                if not invoice_id:
                    vals = self.get_invoice_default_values( cr, uid, contract, context=context )
                    vals.update({'user_id':salesman})
                    invoice_id = invoices.create( cr, salesman, vals, context=context )
                    if not invoice_id: break
                if not invoice:
                    invoice = invoices.browse( cr, uid, invoice_id, context=context )
                    if not invoice:
                        invoice_id = False
                        break

                now = datetime.now().strftime( '%Y-%m-%d' )
                if contract_position.next_invoice_date and contract_position.next_invoice_date > now:
                    continue
                
                # Prepare a new invoice line
                do_it = True
                invoice_line_id = False
                if not contract_position.is_billable:
                    if not eagle_param.make_inv_lines_with_unbillables:
                        do_it = False
                        contract_positions.write( cr, salesman, [contract_position.id], { 'state': 'done' }, context=context )
                if do_it:
                    vals = self.get_invoice_line_default_values( cr, uid, invoice, contract, contract_position, context=context )
                    vals['contract_position_id'] = contract_position.id
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
                                vals['account_analytic_id'] = proj.analytic_account_id.id
                    self.__logger.debug( u"In do_contract_inv_installation(): vals=%s", tools.ustr(vals) )
                    invoice_line_id = invoice_lines.create( cr, salesman, vals, context=context )
                if invoice_line_id:
                    contract_positions.write( cr, salesman, [contract_position.id], { 'state': 'done' }, context=context )
                self.__logger.debug( "In do_contract_inv_installation(): invoice_line_id=%s", str(invoice_line_id) )
            
            # This loop handles the progressive contract positions 
            #    - those already invoiced are skipped
            #    - the others are skipped
            #    - each time an object is correctly added to an invoice, it's marked as invoiced
            for contract_position in contract.positions:
                if contract_position.state != 'progressive' or contract_position.progr_invoiced: continue
                
                # If needed, prepare a new invoice, if not already defined
                if not invoice_id:
                    invoice_ids = invoices.search( cr, uid, [ ('type','=','out_invoice'), ('state', '=', 'draft'), ('contract_id', '=', contract.id) ], context=context )
                    if invoice_ids and len(invoice_ids): invoice_id = invoice_ids[0]
                if not invoice_id:
                    vals = self.get_invoice_default_values( cr, uid, contract, context=context )
                    vals.update({'user_id':salesman})
                    invoice_id = invoices.create( cr, salesman, vals, context=context )
                    if not invoice_id: break
                if not invoice:
                    invoice = invoices.browse( cr, uid, invoice_id, context=context )
                    if not invoice:
                        invoice_id = False
                        break

                now = datetime.now().strftime( '%Y-%m-%d' )
                if contract_position.next_invoice_date and contract_position.next_invoice_date > now:
                    continue
                
                # Prepare a new invoice line
                do_it = True
                invoice_line_id = False
                if not contract_position.is_billable:
                    if not eagle_param.make_inv_lines_with_unbillables:
                        do_it = False
                        vals = { 'progr_invoiced': True }
                        if contract_position.progr_rate >= 100.0:
                            vals['state'] = 'done'
                        contract_positions.write( cr, salesman, [contract_position.id], vals, context=context )
                if do_it:
                    vals = self.get_invoice_line_default_values( cr, uid, invoice, contract, contract_position, context=context )
                    vals['contract_position_id'] = contract_position.id
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
                                vals['account_analytic_id'] = proj.analytic_account_id.id
                    self.__logger.debug( u"In do_contract_inv_installation(): vals=%s", tools.ustr(vals) )
                    invoice_line_id = invoice_lines.create( cr, salesman, vals, context=context )
                if invoice_line_id:
                    vals = { 'progr_invoiced': True }
                    if contract_position.progr_rate >= 100.0:
                        vals['state'] = 'done'
                    contract_positions.write( cr, salesman, [contract_position.id], vals, context=context )
                self.__logger.debug( "In do_contract_inv_installation(): invoice_line_id=%s", str(invoice_line_id) )
            
            if contract.state == 'production':

                # This loop handles recurrent contract positions 
                #    - recurrent products may be put either in the same or in a different invoice, depending on
                #      how much time has passed between the 1st invoice and 1st occurence of the recurrent product
                #    - each time an object is correctly added to an invoice, its state is set to 'done'
                for contract_position in contract.positions:
                    if not contract_position.is_active: continue
                    if not contract_position.recurrence_id: continue
                    if contract_position.state != 'recurrent': continue
                    if not contract_position.next_invoice_date: continue
    
                    recurrence = recurrences.browse( cr, uid, contract_position.recurrence_id.id, context=context )
                    if not recurrence:
                        continue
    
                    now = datetime.now().strftime( '%Y-%m-%d' )
                    next = datetime.strptime( contract_position.next_invoice_date, '%Y-%m-%d' )
                    dt = next - relativedelta( days=contract_position.cancellation_deadline )
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
                        self.__logger.debug( u"Skipping contract position '%s' because of the dates: %s and now we are: %s", (tools.ustr(contract_position.out_description), tools.ustr(before), str(now)) )
                        continue
                    
                    # If needed, prepare a new invoice, if not already defined
                    if not invoice_id:
                        invoice_ids = invoices.search( cr, uid, [ ('type','=','out_invoice'), ('state', '=', 'draft'), ('contract_id', '=', contract.id) ], context=context )
                        if invoice_ids and len(invoice_ids): invoice_id = invoice_ids[0]
                    if not invoice_id:
                        vals = self.get_invoice_default_values( cr, uid, contract, context=context )
                        vals.update({'user_id':salesman})
                        invoice_id = invoices.create( cr, salesman, vals, context=context )
                        if not invoice_id: break
                    if not invoice:
                        invoice = invoices.browse( cr, uid, invoice_id, context=context )
                        if not invoice:
                            invoice_id = False
                            break
                    
                    # Prepare a new invoice line
                    do_it = True
                    invoice_line_id = False
                    if not contract_position.is_billable:
                        if not eagle_param.make_inv_lines_with_unbillables:
                            do_it = False
                            invoice_line_id = True
                    if do_it:
                        vals = self.get_invoice_line_default_values( cr, uid, invoice, contract, contract_position, context=context )
                        vals['contract_position_id'] = contract_position.id
                        if contract.project_id:
                            if use_one_project:
                                proj_use = 'grouping'
                            else:
                                proj_use = 'maint'
                            proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id),('project_use','=',proj_use)], context=context )
                            if not proj_ids or not len( proj_ids ):
                                proj_ids = projects.search( cr, uid, [('contract_id','=',contract.id)], context=context )
                            if proj_ids and len( proj_ids ):
                                proj = projects.browse(cr, uid, proj_ids[0], context=context)
                                if proj and proj.analytic_account_id:
                                    vals['account_analytic_id'] = proj.analytic_account_id.id
                        invoice_line_id = invoice_lines.create( cr, salesman, vals, context=context )
                    if invoice_line_id:
                        txt = contract_position.description + ' - ' + next.strftime( '%d.%m.%Y' ) + ' ' + _( 'to' ) + ' ' + s_after.strftime( '%d.%m.%Y' )
                        contract_positions.write( cr, salesman, [contract_position.id], { 'next_invoice_date': after.strftime( '%Y-%m-%d' ), 'out_description': txt } )

            if invoice:
                if eagle_param and eagle_param.use_prec_invoices:
                    cr.execute('select max(sequence) from account_invoice_line where invoice_id='+str(invoice.id))
                    row = cr.fetchone()
                    seq = row and row[0] or 0
                    invoice_ids = invoices.search( cr, uid, [ ('type','=','out_invoice'), ('state', 'not in', ['draft','canceled']), ('contract_id', '=', contract.id) ], order='number desc', context=context )
                    for inv in invoices.browse(cr, uid, invoice_ids, context=context):
                        seq += 10
                        vals = {
                            'name': 'Deduction: '+inv.number,
                            'origin': contract.name,
                            'invoice_id': invoice.id,
                            'contract_id': contract.id,
                            'sequence': seq,
                            'account_id': inv.account_id.id,                # TODO ???
                            'price_unit': -inv.amount_total,
                            'quantity': 1.0,
                            'invoice_line_tax_id': [(6,0,[])],
                        }
                    invoice_lines.create( cr, salesman, vals, context=context )
            
            if eagle_param and eagle_param.auto_production_state:
                valid = True
                for cnt_line in contract.positions:
                    if cnt_line.state == 'open':
                        valid = False
                        break
                if valid:
                    self.contract_production( cr, salesman, [contract.id], {} )
        
        return True

    # ---------- Interface related

    def button_make_invoice(self, cr, uid, ids, context={}):
        return self.do_contract_inv_installation( cr, uid, ids, context=context, force_invoicing=True )

    # ---------- Scheduler management

    def run_inv_scheduler( self, cr, uid, context={} ):
        ''' Runs Invoices scheduler.
        '''
        if not context:
            context={}
        
        self_name = 'Eagle Invoices Scheduler'
        for contract in self.browse( cr, uid, self.search( cr, uid, [], context=context ), context=context ):
            if contract.state in ['installation','production']:
                self.__logger.debug( u"Checking contract '%s'", tools.ustr(contract.name) )
                self.do_contract_inv_installation( cr, uid, [contract.id], context=context )
        
        return True

eagle_contract()
