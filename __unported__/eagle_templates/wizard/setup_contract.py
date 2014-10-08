# -*- coding: utf-8 -*-
#
#  File: setup_contract.py
#  Module: eagle_templates
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2013 Open-Net Ltd. All rights reserved.
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

from tools.translate import _
from osv import osv, fields
import time

class wiz_copy_tmpl_2_cnt(osv.osv_memory):

    _name = "eagle.wiz_copy_tmpl_2_cnt"
    _description = "Eagle wizard: copy template to contract"

    # ------------ Fields management

    _columns = {
        'name': fields.char('New name', size=64, required=True),
        'customer_id': fields.many2one('res.partner', 'Customer', required=True),
        'date_start': fields.date( 'Next action date' ),
    }
    
    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse(cr, uid, params_obj.search( cr, uid, [], context=context ), context=context):
            return params

        return False

    def _detect_name(self, cr, uid, context={}):
        res = False
        if context is None: context = {}
        if context.get('active_model', '') == 'eagle.contract.meta' and context.get('active_id', False):
            meta_obj = self.pool.get('eagle.contract.meta')
            params = self.__get_eagle_parameters(cr, uid, context=context)
            if getattr(params, 'use_meta_4_name', False):
                meta = meta_obj.browse(cr, uid, context['active_id'], context=context)
                if meta:
                    res = meta_obj.detect_next_contract_name(cr, uid, meta.id, meta.name, getattr(params, 'use_meta_4_name_digits', 3), context=context)
        if not res:
            if self.pool.get('eagle.template.contract') and context.get('active_id', False):
                tmpl = self.pool.get('eagle.template.contract').browse(cr, uid, context['active_id'], context=context)
                if tmpl:
                    res = getattr(tmpl, 'name','')

        return res
    
    _defaults = {
        'name': _detect_name,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
    }

    # ------------ User interface related

    def do_it(self, cr, uid, ids, context=None):
        datas = self.browse(cr, uid, ids[0], context=context)
        
        cnt_vals = {
            'name': datas.name,
            'customer_id': datas.customer_id.id,
        }

        tmpl = False
        if context.get('active_id'):
            tmpl = self.pool.get('eagle.template.contract').read(cr, uid, context['active_id'], ['category_id'], context=context)
            if tmpl and tmpl.get('category_id'):
                cnt_vals['category_id'] = tmpl['category_id'][0]
        
        contracts_obj = self.pool.get('eagle.contract')
        cnt_id = contracts_obj.create(cr, uid, cnt_vals, context=context)
        if not cnt_id:
            return False
        params = self.__get_eagle_parameters(cr, uid, context=context)
        descr_field = getattr(params, 'pos_onchange_prod_field', False)
        
        if tmpl:
            pos_obj = self.pool.get('eagle.contract.position')
            for tmpl_pos in tmpl.positions:
                pos_vals = {}
                res = pos_obj.onchange_product(cr, uid, [], tmpl_pos.name.id, 1.0, datas.date_start, datas.customer_id.id, False)
                if res and res.get('value'):
                    pos_vals.update(res['value'])
                    pos_vals['tax_id'] = [(6, 0, res['value'].get('tax_id', []))]
                pos_vals.update({
                    'name': tmpl_pos.name.id,
                    'contract_id': cnt_id,
                    'recurrence_id': tmpl_pos.recurrence_id and tmpl_pos.recurrence_id.id or False,
                    'state': tmpl_pos.recurrence_id and 'recurrent' or 'open',
                    'cancellation_deadline': tmpl_pos.cancellation_deadline,
                    'is_billable': tmpl_pos.is_billable,
                    'sequence': tmpl_pos.sequence,
                    'notes': getattr(tmpl_pos.name, descr_field and descr_field.name or '', tmpl_pos.notes ),
                })
                
                pos_obj.create(cr, uid, pos_vals, context=context)

        
        if context.get('no_list', False):
            return {}
    
        # Open the contract list with the new one
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'eagle_base', 'eagle_action_contract_filter_all_tree')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = str([('id','=',cnt_id)])                
        
        return result

wiz_copy_tmpl_2_cnt()

class wiz_copy_tmpl_pos_2_cnt(osv.osv_memory):

    _name = "eagle.wiz_copy_tmpl_pos_2_cnt"
    _description = "Eagle wizard: copy template positions to current contract"

    # ------------ Fields management

    _columns = {
        'name': fields.char('New name', size=64, required=True),
        'cnt_tmpl_id': fields.many2one('eagle.template.contract', 'Tempalte', required=True),
        'date_start': fields.date( 'Next action date' ),
    }
    
    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse(cr, uid, params_obj.search( cr, uid, [], context=context ), context=context):
            return params

        return False

    def _detect_name(self, cr, uid, context={}):
        res = ''
        if context is None: context = {}
        if context.get('active_model', '') == 'eagle.contract' and context.get('active_id', False):
            cnt_obj = self.pool.get('eagle.contract')
            cnt = cnt_obj.read(cr, uid, context['active_id'], ['name'], context=context)
            res = cnt and cnt.get('name','') or ''

        return res
    
    _defaults = {
        'name': _detect_name,
        'date_start': lambda *a: time.strftime('%Y-%m-%d'),
    }

    # ------------ User interface related

    def do_it(self, cr, uid, ids, context=None):
        datas = self.browse(cr, uid, ids[0], context=context)
        
        cnt_id = context.get('active_id', False)
        if not cnt_id:
            return {}
        
        cnt = self.pool.get('eagle.contract').browse(cr, uid, cnt_id, context=context)
        if not cnt:
            return {}
        params = self.__get_eagle_parameters(cr, uid, context=context)
        descr_field = getattr(params, 'pos_onchange_prod_field', False)
        
        seq = reduce(lambda x, y: max(x, y), [pos.sequence for pos in cnt.positions], 0)
        pos_obj = self.pool.get('eagle.contract.position')
        for tmpl_pos in datas.cnt_tmpl_id.positions:
            pos_vals = {}
            res = pos_obj.onchange_product(cr, uid, [], tmpl_pos.name.id, 1.0, datas.date_start, cnt.customer_id and cnt.customer_id.id or False, False)
            if res and res.get('value'):
                pos_vals.update(res['value'])
                pos_vals['tax_id'] = [(6, 0, res['value'].get('tax_id', []))]
            pos_vals.update({
                'name': tmpl_pos.name.id,
                'contract_id': cnt_id,
                'recurrence_id': tmpl_pos.recurrence_id and tmpl_pos.recurrence_id.id or False,
                'state': tmpl_pos.recurrence_id and 'recurrent' or 'open',
                'cancellation_deadline': tmpl_pos.cancellation_deadline,
                'is_billable': tmpl_pos.is_billable,
                'sequence': seq + tmpl_pos.sequence,
                'notes': getattr(tmpl_pos.name, descr_field and descr_field.name or '', tmpl_pos.notes ),
            })
            
            pos_obj.create(cr, uid, pos_vals, context=context)

        
        return {}

wiz_copy_tmpl_pos_2_cnt()
