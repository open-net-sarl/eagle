# -*- coding: utf-8 -*-
#
#  File: projects.py
#  Module: eagle_templates
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
from openerp.addons.eagle_project.projects import eagle_project_types

import logging
_logger = logging.getLogger(__name__)

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
    _inherit = 'project.project'

    # ---------- Instances management

    def create(self, cr, uid, values, context={}):
        project_id = super(project, self).create(cr, uid, values, context=context)
        self.check_task_templates(cr, uid, project_id, context=context)
        
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
            if not tt_ids: 
                _logger.debug("No templates found for the use '%s'" % (project['project_use'],))
                continue

            for tt in tt_obj.read(cr, uid, tt_ids, ['name', 'stage_id', 'sequence'], context):
                check = tasks_obj.search(cr, uid, [('name','=',tt['name']),('project_id','=',project['id'])], context=context)
                _logger.debug("Task '%s' already present" % (tt['name'],))
                if check: continue

                task = {
                    'ons_current_user': uid,
                    'ons_date_start': time.strftime('%Y-%m-%d'),
                    'project_id': project['id'],
                    'name': tt['name'],
                    'stage_id': tt['stage_id'] and tt['stage_id'][0] or tasks_obj._get_default_stage_id(cr, uid, context=context),
                    'sequence': tt['sequence'],
                }
                if project.get('contract_id'): task.update({'contract_id': project['contract_id'][0] })

                _logger.debug("About to create a task with "+str(task))
                tasks_obj.create(cr, uid, task, context=context)

        return True            

project()
