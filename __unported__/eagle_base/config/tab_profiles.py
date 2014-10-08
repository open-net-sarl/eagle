# -*- coding: utf-8 -*-
#
#  File: config/tab_profiles.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#  Eagle's Tab management
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
    _name = 'eagle.config.tabs_profile'
    _description = 'Eagle Configuration Tabs Profile'

    # This will hold the list of tabs to manage
    tabs_list = {}
    
    # ---------- Fields related

    _columns = {
        'name': fields.char( 'Profile', size=40 ),
        'opts': fields.text( 'Options' ),
    }
    
    # ---------- Instances management
    
    def __init__(self, pool, cr):
        super(eagle_config_tabs_profile, self).__init__(pool, cr)
        
        module_tabs_list = {
            'positions':'Content',
            'messages':'Messages',
            'other_infos':'Other infos',
            'members':'Contract members',
            'partners':'Contract partners',
            'part_roles':'Contract partners roles',
            'part_contracts_list':"Contracts list in partner's form",
            'notes':'Notes',
            'debug':'Debug',
        }
        for tab in module_tabs_list:
            self.tabs_list.update({tab:'Eagle Base: '+module_tabs_list[tab] })
        
        # Results in something like:
        # {
        #     'partners': 'Eagle Base: Contract partners', 
        #     'members': 'Eagle Base: Contract members', 
        #     'debug': 'Eagle Base: Debug', 
        #     'positions': 'Eagle Base: Content', 
        #     'other_infos': 'Eagle Base: Other infos', 
        #     'messages': 'Eagle Base: Messages', 
        #     'notes': 'Eagle Base: Notes'
        # }

    # ---------- Utilities

    def check_tab(self, cr, uid, prof_ids, tab_name, context={}):
        res = {}
        for profile in self.browse(cr, uid, prof_ids, context=context):
            res[profile.id] = tab_name in profile.opts
        
        return res

eagle_config_tabs_profile()

