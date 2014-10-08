# -*- coding: utf-8 -*-
#
#  File: projects.py
#  Module: eagle_project
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

from osv import fields, osv
import tools
from tools.translate import _
import time

import logging
_logger = logging.getLogger(__name__)

eagle_project_types = [
    ( 'grouping','Grouping' ),
    ( 'inst','Installation' ),
    ( 'maint','Maintenance' ),
]

class task(osv.osv):
    _inherit = "project.task"

    _columns = {
        'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
        'ons_current_user': fields.char( 'Current user', type='char', size=64),
        'ons_date_start': fields.datetime('Start date'),
        'is_in_progress': fields.boolean('Is in progress?'),
        'name': fields.char('Task Summary', size=256, required=True),
    }
    
    def __get_eagle_parameters( self, cr, uid, context={} ):
        params_obj = self.pool.get('eagle.config.params')
        for params in params_obj.browse( cr, uid, params_obj.search(cr, uid, [], context=context ), context=context):
            return params

        return False

    def default_contract(self, cr, uid, context={}):
        if not context.get('current_eagle_project', False): return False
        prj = self.pool.get('project.project').browse(cr, uid, context['current_eagle_project'], context=context)
        return prj and prj.contract_id and prj.contract_id.id or False

    def default_project(self, cr, uid, context={}):
        if not context.get('current_eagle_project', False): return False
        prj = self.pool.get('project.project').browse(cr, uid, context['current_eagle_project'], context=context)
        if not prj or not prj.contract_id: return False

        eagle_param = self.__get_eagle_parameters(cr, uid, context=context)
        use_one_project = eagle_param and eagle_param.use_one_project or False

        cnt = prj.contract_id
        prj_id = False
        for c_prj in cnt.project_ids:
            if c_prj.project_use == 'grouping':
                if use_one_project or (cnt.state not in ['installation','production']):
                    prj_id = c_prj.id
                    break
            if c_prj.project_use == 'inst' and not use_one_project:
                if cnt.state  == 'installation':
                    prj_id = c_prj.id
                    break
            if c_prj.project_use == 'maint' and not use_one_project:
                if cnt.state == 'production':
                    prj_id = c_prj.id
                    break
        return prj_id

    _defaults = {
        'is_in_progress': False,
        'contract_id': default_contract,
        'project_id': default_project,
    }
    
    def in_progress(self, cr, uid, ids, context={}):
        dt_today = time.strftime('%Y-%m-%d %H:%M:%S')
        user_name = self.pool.get('res.users').browse(cr,uid,uid).name
        self.write( cr,uid,ids,{'is_in_progress':True,'ons_current_user':user_name, 'ons_date_start':dt_today} )
        return True

    def stop_progress(self, cr, uid, ids, context={}):
        self.write( cr,uid,ids,{'is_in_progress':False,'ons_current_user':'', 'ons_date_start':False} )
        return True

    def create( self, cr, uid, vals, context=None ):
        eagle_param = self.__get_eagle_parameters(cr, uid, context=context)
        use_one_project = eagle_param and eagle_param.use_one_project or False

        projects = self.pool.get( 'project.project' )
        if 'contract_id' in vals and 'project_id' not in vals:
            cnt = self.pool.get('eagle.contract').read(cr, uid, vals['contract_id'], ['state'], context=context)
            if cnt and cnt.get('state'):
                if use_one_project:
                    proj_use = 'grouping'
                else:
                    proj_use = cnt['state'] == 'installation' and 'inst' or cnt['state'] == 'maintenance' and 'maint' or ''
                if proj_use:
                    proj_ids = projects.search( cr, uid, [('contract_id','=',vals['contract_id']),('project_use','=',proj_use)], context=context )
                    if proj_ids and len( proj_ids ):
                        vals['project_id'] =  proj_ids[0]
        elif 'project_id' in vals and 'contract_id' not in vals:
            proj = projects.read(cr, uid, vals['project_id'], ['contract_id'], context=context)
            if proj and proj.get('contract_id', False):
                vals['contract_id'] = proj['contract_id'][0]
        if 'procurement_id' in vals:
            if vals['procurement_id']:
                pro = self.pool.get( 'procurement.order' ).browse( cr, uid, vals['procurement_id'], context=context )
                if pro and pro.product_id and pro.product_id.product_manager:
                    vals['user_id'] = pro.product_id.product_manager.id
        _logger.debug("About to create a task in the class 'task' with "+str(vals))
        return super( task, self ).create( cr, uid, vals, context=context )

task()

class task_template(osv.osv):
    _name = 'eagle.template.task'
    _description = 'Task template'
    
    _columns = {
        'name': fields.char('Task Summary', size=128, required=True),
        'project_use': fields.selection( eagle_project_types, 'Project Use', required=True ),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of tasks."),
        'stage_id': fields.many2one('project.task.type', 'Stage'),
    }
    
    def _get_default_stage_id(self, cr, uid, context=None):
        return self.pool.get('project.task')._get_default_stage_id(cr, uid, context=context)

    _defaults = {
        'sequence': 10,
        'stage_id': _get_default_stage_id,
    }
    
    _order = 'project_use,sequence'

task_template()

class project(osv.osv):
    _inherit = "project.project"

    # ---------- Fields management
    
    def _retrieve_parent_project( self, cr, uid, prj_ids, name, args, context ):
        res = {}
        aaa_tbl = self.pool.get( 'account.analytic.account' )
        for prj in self.browse( cr, uid, prj_ids, context=context ):
            res[prj.id] = False
            aaa_parent = prj.parent_id    # 
            if aaa_parent and aaa_parent.id:
                cr.execute("Select id from project_project where analytic_account_id=" + str(aaa_parent.id) )
                row = cr.fetchone()
                if row and len( row ) > 0:
                    res[prj.id] = row[0]
        
        return res

    _columns = {
        'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
        'project_use': fields.selection( eagle_project_types, 'Project Use' ),
        'parent_project': fields.function( _retrieve_parent_project, method=True, string="Parent Project", type="many2one", relation="project.project" ),
    }

    # ---------- Instances management

    def create( self, cr, uid, vals, context=None ):
        contract_id = False
        if 'contract_id' in vals:
            contract_id = vals['contract_id']
        if not contract_id:
            analytic_account_id = vals.get('analytic_account_id', False)
            if analytic_account_id:
                cr.execute( "Select parent_id from account_analytic_account Where id=%d" % analytic_account_id )
                row = cr.fetchone()
                if row and len( row ) > 0:
                    cr.execute( "Select contract_id from project_project Where analytic_account_id=%d" % row[0] )
                    row = cr.fetchone()
                    if row and len( row ) > 0:
                        contract_id = row[0]
        if contract_id:
            vals['contract_id'] = contract_id
        
        project_id = super( project, self ).create( cr, uid, vals, context=context )
        _logger.debug( "Project creation: ID=%s", str(project_id) )
        if not project_id: return False
        
        _logger.debug( "Project creation: project use=%s", str(vals.get('project_use', False)) )
        if vals.get('project_use', False):
            task = {
                'ons_current_user': uid,
                'ons_date_start': time.strftime('%Y-%m-%d'),
                'project_id': project_id,
            }

            row = self.read(cr, uid, [project_id], ['contract_id'], context=context)[0]
            if row.get('contract_id'): task.update({'contract_id': row['contract_id'][0] })
            
            tt_obj = self.pool.get('eagle.template.task')
            tt_ids = tt_obj.search(cr, uid, [('project_use','=',vals['project_use'])], context=context)
            if tt_ids:
                tasks_obj = self.pool.get('project.task')
                for tt in tt_obj.read(cr, uid, tt_ids, ['name'], context):
                    check = tasks_obj.search(cr, uid, [('name','=',tt['name']),('project_id','=',project_id)], context=context)
                    if not check:
                        task.update({'name': tt['name']})
                        tasks_obj.create(cr, uid, task, context=context)
        
        return project_id

    # ---------- Utilities

    def check_task_templates(self, cr, uid, prj_ids, context={}):
        if not prj_ids: return False
        if isinstance( prj_ids, (int,long) ): prj_ids = [prj_ids]

        tt_obj = self.pool.get('eagle.template.task')
        tasks_obj = self.pool.get('project.task')

        for project in self.read(cr, uid, prj_ids, ['id', 'name', 'contract_id', 'project_use'], context=context):
            if not project['project_use']: continue
            _logger.debug("Checking tasks tempaltes for the project "+str(project))

            tt_ids = tt_obj.search(cr, uid, [('project_use','=',project['project_use'])], context=context)
            if not tt_ids: continue

            for tt in tt_obj.read(cr, uid, tt_ids, ['name', 'stage_id'], context):
                check = tasks_obj.search(cr, uid, [('name','=',tt['name']),('project_id','=',project['id'])], context=context)
                if check: continue

                task = {
                    'ons_current_user': uid,
                    'ons_date_start': time.strftime('%Y-%m-%d'),
                    'project_id': project['id'],
                }
                if project.get('contract_id'): task.update({'contract_id': project['contract_id'][0] })
                task.update({
                    'name': tt['name'],
                    'stage_id': tt['stage_id'] and tt['stage_id'][0] or tasks_obj._get_default_stage_id(cr, uid, context=context)
                })
                _logger.debug("About to create a task with "+str(task))
                tasks_obj.create(cr, uid, task, context=context)

        return True            

project()

class project_work( osv.osv ):
    _inherit = 'project.task.work'

    _columns = {
        'contract_id': fields.many2one( 'eagle.contract', 'Contract' ),
        'ons_hrtif_to_invoice': fields.many2one('hr_timesheet_invoice.factor', 'Reinvoice Costs', required=True, 
            help="Fill this field if you plan to automatically generate invoices based " \
            "on the costs in this analytic account: timesheets, expenses, ..." \
            "You can configure an automatic invoice rate on analytic accounts."),
        'ons_hrtif_why_chg': fields.char('Why change the factor', size=60),
        'ons_hrtif_changed': fields.boolean('Change the factor?'),
    }

    def _default_hrtif_id(self, cr, uid, context=None):
        cr.execute( "select id from hr_timesheet_invoice_factor order by abs(factor) asc limit 1" )
        row = cr.fetchone()
        ret = False
        if row and row[0]:
            ret = row[0]
        
        return ret

    _defaults = {
        'ons_hrtif_to_invoice': _default_hrtif_id,
    }

    def create(self, cr, uid, vals, *args, **kwargs):
        context = kwargs.get('context', {})
        if not context.get('no_analytic_entry',False):
            if 'task_id' in vals:
                task = self.pool.get('project.task').browse(cr, uid, vals['task_id'], context=context)
                if task:
                    contract_id = task and task.contract_id and task.contract_id.id or False
                    if contract_id:
                        vals.update({'contract_id': contract_id})
        
        if not vals.get('ons_hrtif_to_invoice', False):
            if vals.get('task_id', False):
                task = self.pool.get('project.task').browse(cr, uid, vals['task_id'], context=context)
                if task and task.project_id and task.project_id.to_invoice:
                    vals.update({'ons_hrtif_to_invoice':task.project_id.to_invoice.id})
        ret = super(project_work,self).create(cr, uid, vals, *args, **kwargs)
        if ret and ('ons_hrtif_to_invoice' in vals):
            hr_analytic_timesheet_id = self.read( cr, uid, [ret], ['hr_analytic_timesheet_id'] )[0]['hr_analytic_timesheet_id'][0]
            self.pool.get('hr.analytic.timesheet').write( cr, uid, [hr_analytic_timesheet_id], { 'to_invoice': vals['ons_hrtif_to_invoice']} )
        return ret

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if 'ons_hrtif_to_invoice' in vals:
            if isinstance(ids,(int,long)): ids = [ids]
            for rec in self.read( cr, uid, ids, ['hr_analytic_timesheet_id'] ):
                hr_analytic_timesheet_id = rec['hr_analytic_timesheet_id'][0]
                self.pool.get('hr.analytic.timesheet').write( cr, uid, [hr_analytic_timesheet_id], { 'to_invoice': vals['ons_hrtif_to_invoice']}, context=context )
        return super(project_work,self).write( cr, uid, ids, vals, context=context )

    def button_change_hrtif_yes(self, cr, uid, ids, context={}):
        self.write( cr,uid,ids,{'ons_hrtif_changed':True} )
        return True

    def button_change_hrtif_no(self, cr, uid, ids, context={}):
        self.write( cr,uid,ids,{'ons_hrtif_changed':False} )
        return True

project_work()
