# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_project
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

from osv import fields, osv
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import tools
from tools.translate import _
import decimal_precision as dp
from lxml import etree

import logging
_logger = logging.getLogger(__name__)

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'

    # ---------- Instances management

    def _register_hook(self, cr):
        """ stuff to do right after the registry is built """
        super(eagle_contract, self)._register_hook(cr)
        _logger.info("Registering Eagle Project's events")
        funcs = [ 
            ('inst','do_contract_prj_installation'),
            ]
        for func_item in funcs:
            self.register_event_function( cr, 'Eagle Projects', func_item[0], func_item[1] )

    # ---------- Fields management

    def _get_analytic_account( self, cr, uid, ids, name, args, context ):
        res = {}
        for cnt in self.browse( cr, uid, ids, context=context ):
            res[cnt.id] = False
            if cnt.project_id and cnt.project_id.analytic_account_id:
                res[cnt.id] = cnt.project_id.analytic_account_id.id
        
        return res

    def _get_account_analytic_lines( self, cr, uid, cnt_ids, name, args, context ):
        res = {}
        projects = self.pool.get( 'project.project' )
        for cnt_id in cnt_ids:
            res[cnt_id] = []
            pp_ids = projects.search( cr, uid, [( 'contract_id', '=', cnt_id ), ( 'project_use', '=', 'grouping' )] )
            if pp_ids and len( pp_ids ) > 0:
                lst = []
                for project in projects.browse( cr, uid, pp_ids, context=context ):
                    aaa = project.analytic_account_id
                    if aaa:
                        lst = lst + [x.id for x in aaa.line_ids]
                res[cnt_id] = lst
            pp_ids = projects.search( cr, uid, [( 'contract_id', '=', cnt_id ), ( 'project_use', '=', 'inst' )] )
            if pp_ids and len( pp_ids ) > 0:
                lst = []
                for project in projects.browse( cr, uid, pp_ids, context=context ):
                    aaa = project.analytic_account_id
                    if aaa:
                        lst = lst + [x.id for x in aaa.line_ids]
                res[cnt_id] = res[cnt_id] + lst
            pp_ids = projects.search( cr, uid, [( 'contract_id', '=', cnt_id ), ( 'project_use', '=', 'maint' )] )
            if pp_ids and len( pp_ids ) > 0:
                lst = []
                for project in projects.browse( cr, uid, pp_ids, context=context ):
                    aaa = project.analytic_account_id
                    if aaa:
                        lst = lst + [x.id for x in aaa.line_ids]
                res[cnt_id] = res[cnt_id] + lst
        
        return res
    
    def _store_account_analytic_lines(self, cr, uid, ids, field_name, field_value, arg, context):
        if field_name != 'account_analytic_lines' or not field_value:
            return False
        self.pool.get( 'account.analytic.line' ).write( cr, uid, [field_value[0][1]], field_value[0][2], context=context )
        return True

    def _get_cl_totals_prj( self, cr, uid, cnt_ids, name, args, context={} ):
        res = {}
        for cnt in self.browse( cr, uid, cnt_ids, context=context ):
            tots = { 'c_amount': 0.0, 'c_total': 0.0 }
            for cl in cnt.positions:
                tots['c_amount'] += cl.cl_amount
                tots['c_total'] += cl.cl_total
            tots['c_taxes'] = tots['c_total'] - tots['c_amount']
            res[cnt.id] = tots[ name ]
        
        return res

    def _ca_invoiced_calc(self, cr, uid, cnt_ids, name, arg, context=None):
        cnt_res = {}
        aaa_obj = self.pool.get('account.analytic.account')
        for cnt in self.browse(cr, uid, cnt_ids, context=context):
            cnt_res[cnt.id] = 0.0
            account = cnt.account_analytic_account
            if not account: continue
            ids = [account.id]
            res = {}
            res_final = {}
            child_ids = tuple(aaa_obj.search(cr, uid, [('parent_id', 'child_of', ids)], context=context))
            for i in child_ids:
                res[i] =  {}
                for n in [name]:
                    res[i][n] = 0.0
            if not child_ids:
                return res
    
            if child_ids:
                cr.execute("SELECT account_analytic_line.account_id, COALESCE(SUM(amount), 0.0) \
                        FROM account_analytic_line \
                        JOIN account_analytic_journal \
                            ON account_analytic_line.journal_id = account_analytic_journal.id  \
                        WHERE account_analytic_line.account_id IN %s \
                            AND account_analytic_journal.type = 'sale' \
                        GROUP BY account_analytic_line.account_id", (child_ids,))
                for account_id, sum in cr.fetchall():
                    print " *** _ca_invoiced_calc *** account=",account_id,", sum=",sum
                    res[account_id][name] = round(sum,2)
            data = aaa_obj._compute_level_tree(cr, uid, ids, child_ids, res, [name], context=context)
            for i in data:
                res_final[i] = data[i][name]
            cnt_res[cnt.id] = res_final[ids[0]]
        return cnt_res

    def _remaining_ca_calc(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for cnt in self.browse(cr, uid, ids, context=context):
            res[cnt.id]=0.0
            account = cnt.account_analytic_account
            if not account: continue
            if cnt.c_total != 0:
                res[cnt.id] = cnt.c_total - account.ca_invoiced
        for id in ids:
            res[id] = round(res.get(id, 0.0),2)
        return res
    
    def check_tabs_profile(self, cr, uid, cnt_ids, field_names, args, context={}):
        return super(eagle_contract,self).check_tabs_profile(cr, uid, cnt_ids, field_names, args, context=context)

    _columns = {
        'project_id': fields.many2one( 'project.project', 'Project' ),
        'project_ids': fields.one2many( 'project.project', 'contract_id', 'Project and sub-projects' ),
        'tasks': fields.one2many( 'project.task', 'contract_id', string="Tasks",  domain=[('state','!=','done')] ),
        'works': fields.one2many( 'project.task.work', 'contract_id', 'Contracts works' ),
        'account_analytic_account': fields.function( _get_analytic_account, method=True, type='many2one', obj="account.analytic.account", string="Analytic Account" ),
        'account_analytic_lines': fields.function( _get_account_analytic_lines, fnct_inv=_store_account_analytic_lines, method=True, type='one2many', obj="account.analytic.line", string="Account Analytic Lines" ),
        'ons_hrtif_to_invoice': fields.many2one('hr_timesheet_invoice.factor', 'Reinvoice Costs', required=True, 
            help="Fill this field if you plan to automatically generate invoices based " \
            "on the costs in this analytic account: timesheets, expenses, ..." \
            "You can configure an automatic invoice rate on analytic accounts."),
        'c_amount': fields.function( _get_cl_totals_prj, method=True, type="float", string='Tax-free Amount', digits_compute=dp.get_precision('Sale Price') ),
        'c_taxes': fields.function( _get_cl_totals_prj, method=True, type="float", string='Taxes', digits_compute=dp.get_precision('Sale Price') ),
        'c_total': fields.function( _get_cl_totals_prj, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position'),

        'ca_invoiced': fields.function(_ca_invoiced_calc, method=True, type='float', string='Invoiced Amount',
            help="Total customer invoiced amount for this account.",
            digits_compute=dp.get_precision('Account')),
        'remaining_ca': fields.function(_remaining_ca_calc, method=True, type='float', string='Remaining Revenue',
            help="Computed using the formula: Max Invoice Price - Invoiced Amount.",
            digits_compute=dp.get_precision('Account')),

        'tab_profile_project_tasks': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_project_tasks', multi='tab_profile_project_tasks' ),
        'tab_profile_anal_entries': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_anal_entries', multi='tab_profile_project_tasks' ),
    }

    def _default_hrtif_id(self, cr, uid, context=None):
        cr.execute( "select id from hr_timesheet_invoice_factor order by factor asc limit 1" )
        row = cr.fetchone()
        ret = False
        if row and row[0]:
            ret = row[0]
        
        return ret

    _defaults = {
        'ons_hrtif_to_invoice': _default_hrtif_id,
    }
    
    # ---------- Interface management
    
    def onchange_customer(self, cr, uid, ids, customer_id):
        ret = super(eagle_contract, self).onchange_customer(cr, uid, ids, customer_id)
        if ret.get('value'):
            fiscal_position = False
            if customer_id:
                cust = self.pool.get('res.partner').browse(cr, uid, customer_id)
                fiscal_position = cust and cust.property_account_position and cust.property_account_position.id or False
            ret['value']['fiscal_position'] = fiscal_position
        
        return ret

    # ---------- States management

    def _setup_the_projects( self, cr, uid, ids, context={} ):
        _logger.debug( "About to setup the projects for the contract id %s", str(ids) )

        projects = self.pool.get( 'project.project' )
        aaa_obj = self.pool.get('account.analytic.account')

        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        set_company = eagle_param and eagle_param.set_company or False
        project_privacy_visibility = eagle_param and eagle_param.project_privacy_visibility or 'public'

        if isinstance( ids, (int, long) ):
            ids = [ids]
        
        for cnt in self.browse( cr, uid, ids, context=context ):
            if cnt.project_id:
                continue
            filter = [('code','=','3')]
            if set_company and cnt.company_id:
                filter.append(('company_id', '=', cnt.company_id.id))
            tmp_ids = aaa_obj.search( cr, 1, filter, context=context )
            root_id = tmp_ids and len(tmp_ids) > 0 and tmp_ids[0] or False

            prj_vals = {
                'name': cnt.name,
                'sequence':1,
                'contract_id': cnt.id,
                'partner_id': cnt.customer_id and cnt.customer_id.id or False,
                'project_use': 'grouping',
                'parent_id': root_id,
                'privacy_visibility': project_privacy_visibility,
            }
            if set_company and cnt.company_id:
                prj_vals['company_id'] = cnt.company_id.id
            filter = [
                ('contract_id','=', cnt.id),
                ('project_use','=', 'grouping'),
            ]
            prj_id = projects.search(cr, uid, filter, context=context)
            if prj_id:
                prj_id = prj_id[0]
                _logger.info("PRJ0 updated with: %s", str(prj_vals))
                projects.write(cr, uid, [prj_id], prj_vals, context=context)
            else:
                _logger.info("PRJ0 created with: %s", str(prj_vals))
                prj_id = projects.create(cr, uid, prj_vals, context=context)
                if not prj_id:
                    continue

            # The contract keeps track of the parent project
            self.write(cr, uid, [cnt.id], {'project_id': prj_id})
                
            # Eagle may function with only one project, depending on its configuration
            if not eagle_param.use_one_project:
                # Retrieve the parent project itself to add it two children
                proj = projects.browse(cr, uid, prj_id, context=context)
                parent_acc_id = proj and proj.analytic_account_id and proj.analytic_account_id.id or False
    
                # Build a new sub-project for the installation process
                prj_vals = {
                    'name': cnt.name + ' - ' + _( 'Installation' ),
                    'sequence':2,
                    'contract_id': cnt.id,
                    'partner_id': cnt.customer_id and cnt.customer_id.id or False,
                    'project_use': 'inst',
                    'privacy_visibility': project_privacy_visibility,
                }
                if set_company and cnt.company_id:
                    prj_vals['company_id'] = cnt.company_id.id

                filter = [
                    ('contract_id','=', cnt.id),
                    ('project_use','=', 'inst'),
                ]
                p_id1 = projects.search(cr, uid, filter, context=context)
                if p_id1:
                    p_id1 = p_id1[0]
                    _logger.info("PRJ1 updated with: %s", str(prj_vals))
                    projects.write(cr, uid, [prj_id], prj_vals, context=context)
                else:
                    _logger.debug( "PRJ1 created with: %s", str(prj_vals) )
                    p_id1 = projects.create( cr, uid, prj_vals )
                
                # Build a new sub-project for the maintenance process
                prj_vals = {
                    'name': cnt.name + ' - ' + _( 'Maintenance' ),
                    'sequence':3,
                    'contract_id': cnt.id,
                    'partner_id': cnt.customer_id and cnt.customer_id.id or False,
                    'project_use': 'maint',
                    'privacy_visibility': project_privacy_visibility,
                }
                if set_company and cnt.company_id:
                    prj_vals['company_id'] = cnt.company_id.id

                filter = [
                    ('contract_id','=', cnt.id),
                    ('project_use','=', 'maint'),
                ]
                p_id2 = projects.search(cr, uid, filter, context=context)
                if p_id2:
                    p_id2 = p_id2[0]
                    _logger.info("PRJ2 updated with: %s", str(prj_vals))
                    projects.write(cr, uid, [prj_id], prj_vals, context=context)
                else:
                    _logger.debug( "PRJ2 created with: %s", str(prj_vals) )
                    p_id2 = projects.create( cr, uid, prj_vals, context=context )
    
                # Link the two new children to their common parent
                projects.write( cr, uid, [p_id1, p_id2], {'parent_id': parent_acc_id}, context=context )
        
        return True

    # Start the installation
    def do_contract_prj_installation( self, cr, uid, cnt_ids, context={} ):
        _logger.debug( "do_contract_prj_installation() called" )
        if isinstance( cnt_ids, (int,long) ): cnt_ids = [cnt_ids]

        for cnt_id in cnt_ids:
            self._setup_the_projects( cr, uid, cnt_id, context=context )

        return True

eagle_contract()

class eagle_contract_pos( osv.osv ):
    _inherit = 'eagle.contract.position'

    # ---------- Fields management

    def _amount_line_prj(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}

        if field_name == 'cl_amount':
            for line in self.browse(cr, uid, ids, context=context):
                if line.is_billable:
                    price = line.list_price
                    if line.discount:
                        price *= (100 - line.discount) / 100.0
                    res[line.id] = price * line.qty
                else:
                    res[line.id] = 0.0
        else:
            tax_obj = self.pool.get('account.tax')
            cur_obj = self.pool.get('res.currency')
            fpos_obj = self.pool.get('account.fiscal.position')
            for line in self.browse(cr, uid, ids, context=context):
                if line.is_billable:
                    price = line.list_price
                    if line.state == 'progressive':
                        price *= line.progr_rate / 100.0
                    if line.discount:
                        price *= (100 - line.discount) / 100.0
                    
                    tax_id = line.tax_id
                    if line.contract_id.fiscal_position:
                        tax_id = tax_obj.browse(cr, uid, fpos_obj.map_tax(cr, uid, line.contract_id.fiscal_position, line.name.taxes_id))
                    taxes = tax_obj.compute_all(cr, uid, tax_id, price, line.qty, None, line.name, line.contract_id.customer_id)
                    
                    cur = line.contract_id.pricelist_id and line.contract_id.pricelist_id.currency_id or False
                    res[line.id] = cur and cur_obj.round(cr, uid, cur, taxes['total_included']) or taxes['total_included']
                    if field_name == 'cl_taxes':
                       res[line.id] = res[line.id] - price * line.qty
                else:
                    res[line.id] = 0.0

        return res

    _columns = {
        'cl_amount': fields.function( _amount_line_prj, method=True, type="float", string='Tax-free Amount', digits_compute=dp.get_precision('Sale Price') ),
        'cl_taxes': fields.function( _amount_line_prj, method=True, type="float", string='Tax Amount', digits_compute=dp.get_precision('Sale Price') ),
        'cl_total': fields.function( _amount_line_prj, method=True, type="float", string='Total', digits_compute=dp.get_precision('Sale Price') ),
        'tax_id': fields.many2many('account.tax', 'eagle_contrat_line_tax', 'cnt_line_id', 'tax_id', 'Taxes'),
    }

    # ---------- Interface related

    def recomp_line(self, cr, uid, ids, product, customer, qty, list_price, discount, tax_id, fiscal_position):
        if not product or not customer: return False

        real_list_price = list_price
        if discount:
            real_list_price *= (100 - discount) / 100.0

        tax_free = qty * real_list_price
        tax_obj = self.pool.get('account.tax')
        taxes = []
        if fiscal_position and product:
            prod = self.pool.get('product.product').browse(cr, uid, product)
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)
            tax_id =  self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, prod.taxes_id)
        if tax_id and isinstance(tax_id,list):
            _logger.debug( "About to handle the taxes with tax_id=%s", str(tax_id) )
            if isinstance(tax_id[0],(list,tuple)) and len(tax_id[0]) == 3 and isinstance(tax_id[0][2], list):
                if len(tax_id[0][2]):
                    taxes = tax_obj.browse(cr, uid,  tax_id[0][2])
            else:
                taxes = tax_obj.browse(cr, uid, tax_id )

        res = tax_obj.compute_all(cr, uid, taxes, real_list_price, qty, None, product, customer)
        
        return { 'value': {
            'cl_amount': tax_free,
            'cl_taxes': res['total_included'] - tax_free,
            'cl_total': res['total_included'],
        } }

    def recomp_line_sw2(self, cr, uid, ids, contract_id, product, qty, list_price, discount, tax_id):
        if not product or not contract_id: return False

        contract = self.pool.get('eagle.contract').read(cr, uid, contract_id, ['customer_id'])
        customer_id = contract and contract.get('customer_id', False) or False
        if customer_id: customer_id = customer_id[0]
        
        return self.recomp_line(cr, uid, ids, product, customer_id, qty, list_price, discount, tax_id, contract.fiscal_position)

    def onchange_product(self, cr, uid, ids, product_id, qty, date_start, partner_id, pricelist_id, start_of_period=False, fiscal_position=False):
        if not product_id:
            return { 'value': {} }
        res = super( eagle_contract_pos, self ).onchange_product( cr, uid, ids, product_id, qty, date_start, partner_id, pricelist_id, start_of_period=start_of_period )
        if not qty or qty == 0.0:
            qty = res['value']['qty']

        # 2014-07-10: fiscal position are managed now
        #fpos = False        # for now, as of 24 june 2011, fiscal position is ignored
        prod = self.pool.get('product.product').browse(cr, uid, product_id)
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        res['value']['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, prod.taxes_id)
        if 'list_price' in res['value']:
            res['value'].update( { 'cl_amount': qty * res['value']['list_price'] } )
            vals = self.recomp_line(cr, uid, [], product_id, partner_id, qty, res['value']['list_price'], 0.0, res['value']['tax_id'], fiscal_position)
            if vals and vals.get('value'):
                res['value'].update( { 'cl_total': vals['value'].get('cl_total',0.0) } )

        prod = self.pool.get('product.product').browse(cr, uid, product_id)
        delay = prod.sale_delay or False
        if prod.type == 'product':
            if prod.supply_method == 'buy':
                delay = prod.sale_delay
                if prod.seller_ids and len(prod.seller_ids) > 0:
                    suppl = prod.seller_ids[0]
                    delay = suppl.delay
            else:    # prod.supply_method == 'produce'
                delay = prod.produce_delay
        elif prod.type == 'service':
            uom = prod.uom_id
            q = 1.0
            if uom and uom.factor_inv != 0.0:
                q = uom.factor_inv
            delay = qty * q
        res['value'].update( { 'product_duration': delay } )

        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(eagle_contract_pos, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if view_type in ['tree','form']:
            eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
            use_price = True
            if eagle_param:
                use_price = eagle_param.use_price
            if not use_price:
                eview = etree.fromstring(res['arch'])
                found = False
                for field_name in ['cl_amount','cl_taxes']:
                    field = eview.xpath("//field[@name='%s']" % (field_name,) )
                    if not field:
                        continue
                    found = True
                    field[0].set('invisible','1')
                    field[0].set('modifiers', field[0].get('modifiers').replace('false', 'true'))
                if found:
                    res['arch'] = etree.tostring(eview)

        return res

eagle_contract_pos()
