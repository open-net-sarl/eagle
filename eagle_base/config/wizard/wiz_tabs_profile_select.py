# -*- coding: utf-8 -*-
#
#  File: config/wizard/wiz_tabs_profile_select.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#   Starting the version 5.0, this tabs profile wizard is using
#   OE's standard mecanism to implement a completely dynamic fields list management
#   This has been introduced since the old wizard.interface class has been deprecated. 
#
#  Copyright (c) 2011-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class EagleWizTabsProfileSelect(models.TransientModel):
    _name = 'eagle.wiz_tabs_profile_select'
    _description = 'Eagle wizard: select a tabs profile'

    # ---------- Fields management

    @api.model
    def _default_profile(self):
        return self.env['eagle.contract'].get_current_tabs_profile_name()
    
    tabs_prof_id = fields.Many2one('eagle.config.tabs_profile', string='Select your tabs profile (let empty to use the default one)', default=_default_profile)
    
    # ---------- Interface related
    
    @api.one
    def do_save(self):
        
        tabs_prod_id = self.tabs_prof_id and self.tabs_prof_id.id or False
        self.env.user.write({'eagle_tabs_profile': tabs_prod_id})
        return {}
        
