# -*- coding: utf-8 -*-
#
#  File: config/models/tab_profiles.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  Eagle's Tab management
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class eagle_config_tabs_profile(models.Model):
    _inherit = 'eagle.config.tabs_profile'

    # ---------- Instances management
    
    def __init__(self, pool, cr):
        super(eagle_config_tabs_profile,self).__init__(pool, cr)
        
        module_tabs_list = {
            'curr_sol': _('Current Sale Order Lines'),
            'past_sol': _('Past Sale Order Lines'),
            'sale_subscr': _('Sale Subscriptions'),
            'sale_subscrl': _('Sale Subscription Lines'),
            'tasks': _('Tasks'),
            'an_lines': _('Analytic Lines'),
        }
        for tab in module_tabs_list:
            self.tabs_list.update({tab:'Eagle Project: ' + _(module_tabs_list[tab])})

