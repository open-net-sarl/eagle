# -*- encoding: utf-8 -*-
#
#  File: config/wizard/wiz_inv_scheduler.py
#  Module: eagle_management
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011-TODAY Open-Net Ltd. All rights reserved.
##############################################################################
#
# Author Yvon Philippe Crittin / Open Net Sarl
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from openerp import models, fields, api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

class wizard_setup_management_scheduler(models.TransientModel):
    _name = 'eagle.setup_prj_sched'
    _description = 'Setup an Eagle Project Scheduler'
    _cron_filter = [('model','=','eagle.contract'),('function','=','run_prj_scheduler')]

    # ---------- Fields management

    @api.model
    def _default_scheduler_presence(self):
        crons = self.env['ir.cron']
        for cron_id in crons.search(self._cron_filter, limit=1):
            return True
        
        return False
    
    scheduler_present = fields.Boolean('Does the scheduler already exist?', readonly=True, default=_default_scheduler_presence)
    
    @api.multi
    def setup_scheduler(self):
        
        cron_obj = self.env['ir.cron']
        crons = cron_obj.search(self._cron_filter, limit=1)
        if not crons:
            vals = {
                'model': 'eagle.contract',
                'function': 'run_prj_scheduler',
                'name': 'Eagle Project Scheduler',
                'interval_number': 1,
                'interval_type': 'days',
                'numbercall':-1,
                'nextcall': time.strftime('%Y-%m-%d 23:00:00'),
                'args': '()',
                'user_id': SUPERUSER_ID,
            }
            res = cron_obj.create(vals)

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
