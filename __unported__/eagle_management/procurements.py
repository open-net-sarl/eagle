# -*- coding: utf-8 -*-
#
#  File: procurements.py
#  Module: eagle_contracts
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

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    # ---------- Fields management

    _columns = {
        'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
    }

mrp_production()

class procurement_order( osv.osv ):
    _inherit = 'procurement.order'
    
    # ---------- Fields management

    _columns = {
        'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
    }
    
    # ---------- Workflows related

    def _get_project(self, cr, uid, procurement, context=None):
        project = super(procurement_order, self)._get_project(cr, uid, procurement, context=context)

        if procurement.contract_id and procurement.contract_id.project_id:
            project = procurement.contract_id.project_id

        return project

    def action_produce_assign_service(self, cr, uid, ids, context=None):
        task_id = False
        project_task = self.pool.get('project.task')
        for procurement in self.browse(cr, uid, ids, context=context):
            task_id = super(procurement_order, self).action_produce_assign_service(cr, uid, [procurement.id], context=context)
            if task_id and procurement.note:
                project_task.write(cr, uid, [task_id], {'notes': procurement.note},context=context)
        
        return task_id

    def make_po(self, cr, uid, ids, context=None):
        res = super( procurement_order , self).make_po(cr, uid, ids, context=context) 
        purchases = self.pool.get( 'purchase.order' )
        if res and len(res):
            for proc_id in res:
                proc = self.browse( cr, uid, proc_id, context=context )
                if proc.contract_id and proc.purchase_id:
                    purchases.write( cr, uid, [proc.purchase_id.id], { 'contract_id': proc.contract_id.id, 'company_id': proc.contract_id.company_id.id } ) 
        return res

    def make_mo(self, cr, uid, ids, context=None):
        res = super( procurement_order, self).make_mo(cr, uid, ids, context=context) 
        productions = self.pool.get('mrp.production')
        if res and len(res):
            for proc_id in res.keys():
                proc = self.browse( cr, uid, proc_id, context=context )
                if proc.contract_id:
                    productions.write( cr, uid, [res[proc_id]], { 'contract_id': proc.contract_id.id, 'company_id': proc.contract_id.company_id.id } )
        return res

procurement_order()

