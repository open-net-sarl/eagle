# -*- coding: utf-8 -*-
#
#  File: config/models/tab_profiles.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#  Eagle's Tab management
#
#  Copyright (c) 2011-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class eagle_config_tabs_profile(models.Model):
    _name = 'eagle.config.tabs_profile'
    _description = 'Eagle Configuration Tabs Profile'

    # This will hold the list of tabs to manage
    tabs_list = {}
    
    # ---------- Fields related

    name = fields.Char(string='Profile')
    opts = fields.Text(string='Options')
    
    # ---------- Instances management
    
    def __init__(self, pool, cr):
        super(eagle_config_tabs_profile, self).__init__(pool, cr)
        
        module_tabs_list = {
            'other_infos': _('Other infos'),
            'part_contracts_list': _("Files list in partner's form"),
        }
        for tab in module_tabs_list:
            self.tabs_list.update({tab:'Eagle Base: ' + _(module_tabs_list[tab]) })
        
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

