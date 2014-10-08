# -*- coding: utf-8 -*-
#
#  File: wizard/wiz_copy_to.py
#  Module: ons_productivity_edoctree
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2012 Open-Net Ltd. All rights reserved.
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

import logging
_logger = logging.getLogger(__name__)

class wiz_edt_move_to(osv.osv_memory):

    _name = "eagle_edoctree.wiz_move_to"
    _description = "Eagle eDocTree wizard for node move"

    # ------------ Fields management

    _columns = {
        'cnt_src': fields.many2one('eagle.contract', 'Source contract'),
        'nod_target': fields.many2one('ons.edoctree.node', 'Node target'),

        'name': fields.char('New name', size=50),
        'cnt_name': fields.char('New name', size=50),
        'part_name': fields.many2one('res.partner', 'Partner'),
        'source': fields.many2one('eagle.contract', 'Contract'),
        'meta': fields.related('source', 'meta_id', relation='eagle.contract.meta', type='many2one', string='Meta', readonly=True),
        'target': fields.many2one('ons.edoctree.node', 'Target'),
    }
    
    _defaults = {
        'source': lambda s, c, u, ctx: ctx.get('current_contract_id', False),
        'cnt_src': lambda s, c, u, ctx: ctx.get('current_contract_id', False)
    }
    
    # ------------ User interface related

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):

        if context is None:
            context = {}

        result = super(wiz_edt_move_to, self).fields_view_get(cr, uid, view_id,view_type,context=context,toolbar=toolbar,submenu=submenu)

        if view_type == 'form':
            current_id = context.get('current_contract_id', False)
            if current_id:
                cnt = self.pool.get('eagle.contract').read(cr, uid, current_id, ['edoctree_root_id'], context=context)
                if cnt and cnt.get('edoctree_root_id', False):
                    result['fields']['target']['domain'] = ['|',('id','=',cnt['edoctree_root_id'][0]),('parent_id','=',cnt['edoctree_root_id'][0])]
                    result['fields']['nod_target']['domain'] = ['|',('id','=',cnt['edoctree_root_id'][0]),('parent_id','=',cnt['edoctree_root_id'][0])]
        
        return result

    def do_it(self, cr, uid, ids, context=None):
        datas = self.read(cr, uid, ids[0], [], context=context)
        if datas.get('nod_target', False) and context.get('active_id', False):
            self.pool.get('ons.edoctree.node').write(cr, uid, [context['active_id']], {'parent_id':datas['nod_target'][0]}, context=context)
            return {}
        if datas.get('target', False) and context.get('active_id', False):
            self.pool.get('ons.edoctree.node').write(cr, uid, [context['active_id']], {'parent_id':datas['target'][0]}, context=context)
            return {}

        return False

    def on_change_source(self, cr, uid, ids, source):
        ret = { 'meta': False }
        if source:
            src = self.pool.get('eagle.contract').read(cr, uid, source, ['meta_id'])
            if src and src.get('meta_id', False):
                ret['meta'] = src['meta_id'][0]
        return { 'value': ret }

    def contract_create(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0])
        if not data:
            return False
        if context.get('active_id') and data.cnt_name and data.part_name:
            meta_id = False
            names = data.cnt_name.split('-')
            if len(names) > 1:
                meta_id = self.pool.get('eagle.contract.meta').create(cr, uid, {'name':names[0]})
            new_id = self.pool.get('eagle.contract').create(cr, uid, {'name':data.cnt_name, 'customer_id': data.part_name.id, 'meta_id': meta_id}, context=context)
            self.write(cr, uid, ids[0], {'source':new_id}, context=context)
            self.pool.get('ons.edoctree.node').write(cr, uid, [context['active_id']], {'contract_id':new_id}, context=context)
            ctx = context.copy()
            ctx['current_contract_id'] = new_id
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'eagle_edoctree.wiz_move_to',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': data.id,
                'views': [(False, 'form')],
                'target': 'new',
                'context': str(ctx)
            }
        
        return False

wiz_edt_move_to()
