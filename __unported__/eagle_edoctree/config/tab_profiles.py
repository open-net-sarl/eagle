# -*- coding: utf-8 -*-
#
#  File: config/tab_profiles.py
#  Module: eagle_edoctree
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

class eagle_config_tabs_profile( osv.osv ):
    _inherit = 'eagle.config.tabs_profile'

    # ---------- Instances management
    
    def __init__(self, pool, cr):
        super(eagle_config_tabs_profile, self).__init__(pool, cr)
        
        module_tabs_list = {
            'edoctree_c':'Contracts',
            'edoctree_m':'Meta-contracts',
        }
        for tab in module_tabs_list:
            self.tabs_list.update({tab:'Eagle eDocTree: '+module_tabs_list[tab] })
        
eagle_config_tabs_profile()
