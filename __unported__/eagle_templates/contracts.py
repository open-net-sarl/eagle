# -*- coding: utf-8 -*-
#
#  File: contracts.py
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

from osv import fields, osv
from tools.translate import _

import logging
_logger = logging.getLogger('eagle_project_contracts')

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'

    # ---------- Instances management

    def _register_hook(self, cr):
        """ stuff to do right after the registry is built """
        super(eagle_contract, self)._register_hook(cr)
        _logger.info("Registering Eagle Template's events")
        funcs = [ 
            ('inst','do_contract_tmpl_installation'),
            ('prod','do_contract_tmpl_production'),
            ]
        for func_item in funcs:
            self.register_event_function( cr, 'Eagle Projects', func_item[0], func_item[1] )

    # ---------- Interface related
    
    def action_check_task_templates(self, cr, uid, cnt_ids, context={}):
        if isinstance( cnt_ids, (int,long) ): cnt_ids = [cnt_ids]

        proj_obj = self.pool.get('project.project')
        for cnt in self.read(cr, uid, cnt_ids, ['project_ids'], context=context):
            proj_obj.check_task_templates(cr, uid, cnt.get('project_ids', []), context=context)
           
        return True    

    # ---------- Instances management
    
    # Start the installation
    def do_contract_tmpl_installation(self, cr, uid, ids, context={}):
        for cnt in self.read(cr, uid, ids, ['project_ids'], context=context):
            if cnt.get('project_ids'):
                self.pool.get('project.project').check_task_templates(cr, uid, cnt['project_ids'], context=context)

        return True

    # Start the production
    def do_contract_tmpl_production( self, cr, uid, ids, context={}):
        for cnt in self.read(cr, uid, ids, ['project_ids'], context=context):
            if cnt.get('project_ids'):
                self.pool.get('project.project').check_task_templates(cr, uid, cnt['project_ids'], context=context)

        return True

eagle_contract()

class eagle_template_contract_base(osv.osv):
    _name = 'eagle.template.contract'
    _description = 'Eagle contract template'

    # ---------- Fields management

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'category_id': fields.many2one( 'eagle.contract.category', 'Category' ),
    }

eagle_template_contract_base()

class eagle_template_position(osv.osv):
    _name = 'eagle.template.position'
    _description = 'Eagle position template'
    _order = 'template_id,sequence'

    # ---------- Fields management

    _columns = {
        'name': fields.many2one( 'product.product', 'Product', required=True ),
        'template_id': fields.many2one( 'eagle.template.contract', 'Contract', required=True ),
        'recurrence_id': fields.many2one( 'product.recurrence.unit', 'Recurrence' ),
        'cancellation_deadline': fields.integer( 'Days before' ),
        'is_billable': fields.boolean( 'Billable?' ),
        'sequence': fields.integer('Sequence'),
        'notes': fields.text( 'Notes', translate=True ),
    }

eagle_template_position()

class eagle_template_contract(osv.osv):
    _inherit = 'eagle.template.contract'

    # ---------- Fields management

    _columns = {
        'positions': fields.one2many('eagle.template.position', 'template_id', 'Positions'),
    }

eagle_template_contract()
