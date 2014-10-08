# -*- coding: utf-8 -*-
#
#  File: config/config.py
#  Module: eagle_meta
#  Eagle's config management
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from operator import itemgetter
from openerp import SUPERUSER_ID
import time

import logging
_logger = logging.getLogger(__name__)

class eagle_config_params( osv.osv ):
    _inherit = 'eagle.config.params'
    
    # ---------- Fields management

    _columns = {
        'auto_reminder_flag': fields.boolean('Compute'),
        'auto_reminder_delay': fields.integer('Nb of days'),
        'weekly_reminder_flag': fields.boolean('Weekly reminder'),
    }
    
    _defaults = {
        'auto_reminder_flag': lambda *a: False,
        'auto_reminder_delay': lambda *a: 14,
        'weekly_reminder_flag': lambda *a: False,
    }

eagle_config_params()

class eagle_config_settings(osv.osv):
    _inherit = 'eagle.config.settings'

    # ---------- Fields management

    _columns = {
        'auto_reminder_flag': fields.boolean('Compute'),
        'auto_reminder_delay': fields.integer('Nb of days'),
        'weekly_reminder_flag': fields.boolean('Weekly reminder'),
    }

    _defaults = {
        'auto_reminder_flag': lambda *a: False,
        'auto_reminder_delay': lambda *a: 14,
        'weekly_reminder_flag': lambda *a: False,
    }

    # ---------- Interface management
    
    def open_schedulers_list(self, cr, uid, ids, context={}):
        datas = self.read(cr, uid, ids[0], ['auto_reminder_flag', 'auto_reminder_delay'], context=context)
        if not datas:
            flag = False
            delay = 14
        else:
            flag = datas.get('auto_reminder_flag', False)
            delay = datas.get('auto_reminder_delay', 14)

        ctx = context.copy()
        ctx['active_test'] = False
        crons = self.pool.get('ir.cron')
        cron_ids = crons.search(cr, uid, [('model','=','eagle.contract'),('function','=','run_manual_reminders')], context=ctx)
        if not cron_ids or len(cron_ids) < 1:
            vals = {
                'model': 'eagle.contract',
                'function': 'run_manual_reminders',
                'name': 'Eagle CRM Automatic Reminder Scheduler',
                'interval_number': 7,
                'interval_type': 'days',
                'numbercall':-1,
                'nextcall': time.strftime('%Y-%m-%d 23:00:00'),
                'args': '(7,)',
                'user_id': SUPERUSER_ID,
                'active': flag,
            }
            res = crons.create(cr, uid, vals, context=context)
        else:
            vals = {
                'active': flag,
            }
            res = crons.write(cr, uid, cron_ids, vals, context=context)

        res = {
            'domain': str([]),
            'name': 'Crons',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.cron',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'active_test': False},
        }
        return res

    
    def update_auto_reminders(self, cr, uid, ids, context={}):
        datas = self.read(cr, uid, ids[0], ['auto_reminder_flag', 'auto_reminder_delay'], context=context)
        if not datas:
            return False

        delay = datas.get('auto_reminder_delay', 0)
        if not delay:
            return False

        # 1st update: the auto reminder
        query = "Update eagle_contract set auto_reminder_date=(write_date::date + interval '%d days')::date where write_date is not null and state in ('draft','confirm')" % delay
        cr.execute(query)
        # then: current = first date between the automatic and the manual reminder, for those with a manual reminder
        query = 'Update eagle_contract set current_reminder= case when auto_reminder_date::timestamp > reminder_timestamp then reminder_timestamp else auto_reminder_date::timestamp end where reminder_flag is true and state in %s'
        cr.execute(query, (('draft','confirm'),))
        # in the end: current = automatic for those with no manual reminder
        query = 'Update eagle_contract set current_reminder=auto_reminder_date where reminder_flag is not true and state in %s'
        cr.execute(query, (('draft','confirm'),))
        
        return True

eagle_config_settings()
 
