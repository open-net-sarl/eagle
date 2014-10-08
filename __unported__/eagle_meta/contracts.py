# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_meta
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
from lxml import etree

import logging
_logger = logging.getLogger(__name__)

class eagle_meta( osv.osv ):
    _name = 'eagle.contract.meta'
    _description = 'Eagle View Meta Contract'
    
    # ---------- Instances management

    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            return params

        return False
    
    def _eagle_params( self, cr, uid, cnt_ids, field_name, args, context={} ):
        res = {}
        val = False
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if field_name == 'eagle_parm_show_all_meta_tabs':
            val = False
            if eagle_param:
                val = eagle_param.show_all_meta_tabs
                
        if not cnt_ids:
            res = val
        else:
            for cnt_id in cnt_ids:
                res[cnt_id] = val

        return res
        
    # ---------- Fields management

    _columns = {
        'name': fields.char( 'Name', size=64 ),
        'contracts': fields.one2many( 'eagle.contract', 'meta_id', 'Contracts' ),
        'date': fields.date('date'),
        'notes': fields.text('Notes'),
        
        'templates_installed': fields.boolean('Eagle template installed?', readonly=True),
        'eagle_parm_show_all_meta_tabs': fields.function( _eagle_params, method=True, type='boolean', string="Show all meta-tabs?" ),
    }
    
    def _get_default_name(self, cr, uid, context={}):
        new_name = _('No name')
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if eagle_param and eagle_param.use_meta_seq:
            obj_sequence = self.pool.get('ir.sequence')
            new_name = obj_sequence.next_by_code(cr, uid, 'eagle.contract.meta', context=context)
        
        return new_name

    _defaults = {
        'templates_installed': lambda s,c,u,ct: s.pool.get('eagle.template') != None,
        'name': _get_default_name,
    }
    
    _order = 'id desc'

    # ---------- Interface Management

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(eagle_meta, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if view_type != 'form':
            return res
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if eagle_param and eagle_param.meta_mandatory:
            eview = etree.fromstring(res['arch'])
            nodes = eview.xpath("//tree[@name='contracts_list']")
            if nodes:
                nodes[0].set('create', 'false')
                res['arch'] = etree.tostring(eview)
        
        return res

    def call_cnt_tmpl_wizard(self, cr, uid, ids, context={} ):
        if isinstance(ids, (int,long)): ids = [ids]

        mod_obj = self.pool.get('ir.model.data')
        result = False
        try:
          result = mod_obj.get_object_reference(cr, uid, 'eagle_templates', 'wiz_copy_tmpl_2_cnt_action')
        except:
            pass
        if not result: return False
        act_id = result and result[1] or False

        act_obj = self.pool.get('ir.actions.act_window')
        result = act_obj.read(cr, uid, [act_id], context=context)[0]
        if not result.get('context', {}):
            ctx = {}
        else:
            ctx = eval(result['context'])
        ctx.update({
            'default_meta_id': ids[0],
            'no_list': True,
        })
        result['context'] = str(ctx)
        
        return result

    # ---------- Interface related
    
    def detect_next_contract_name(self, cr, uid, meta_id, meta_name, nb_digits, context={}):
        res = False
        if not meta_id: return res
        cr.execute("select name from eagle_contract where meta_id="+str(meta_id)+" order by name desc limit 1")
        row = cr.fetchone()
        if not row or not row[0]:
            suffix = 1
        else:
            test = row[0][-nb_digits:]
            try:
                suffix = int(test) + 1
            except:
                suffix = 1

        format = '-%0'+str(nb_digits)+'d'
        res = meta_name + (format % suffix)
        
        return res

eagle_meta()

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'

    # ---------- Fields management
    
    def _detect_meta_mandatory(self, cr, uid, ids, field_name, arg, context=None):
        eagle_param = self.__get_eagle_parameters(cr, uid, context=context)
        if isinstance(ids, (int,long)): ids = [ids]
        return dict([(x, eagle_param.meta_mandatory) for x in ids])

    _columns = {
        'meta_id': fields.many2one( 'eagle.contract.meta', 'Linked to' ),
        'is_meta_mandatory': fields.function(_detect_meta_mandatory, method=True, type='boolean', string='Meta is mandatory', readonly=True),
    }

    def _get_default_name(self, cr, uid, context={}):
        new_name = _('No name')
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if eagle_param:
            if eagle_param.use_meta_seq:
                obj_sequence = self.pool.get('ir.sequence')
                new_name = obj_sequence.next_by_code(cr, uid, 'eagle.contract', context=context)
        
        return new_name
    
    _defaults = {
        'name': _get_default_name,
    }

    # ---------- Instances management 
       
    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse(cr, uid, params_obj.search( cr, uid, [], context=context ), context=context):
            return params

        return False
    
    def create(self, cr, uid, vals, context=None):
        ret_id = super( eagle_contract, self ).create( cr, uid, vals, context=context )
        return ret_id

    def write(self, cr, uid, cnt_ids, vals, context=None):
        return super(eagle_contract,self).write(cr, uid, cnt_ids, vals, context=context)
    
    def unlink(self, cr, uid, cnt_ids, context=None):
        if context.get('no_store_function', False):
            if isinstance(cnt_ids, (int,long)): cnt_ids = [cnt_ids]
            self.write(cr, uid, cnt_ids, {'meta_id':False}, context=context)
            return True
        return super(eagle_contract,self).unlink(cr, uid, cnt_ids, context=context)
    
    # ---------- Interface management
       
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(eagle_contract, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        if view_type not in ['form','tree']:
            return res
        eagle_param = self.__get_eagle_parameters( cr, uid, context=context )
        if eagle_param and eagle_param.meta_mandatory:
            eview = etree.fromstring(res['arch'])
            nodes = eview.xpath("//" + view_type)
            if nodes:
                nodes[0].set('create', 'false')
                res['arch'] = etree.tostring(eview)
        
        return res

eagle_contract()
