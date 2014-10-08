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

import logging
_logger = logging.getLogger(__name__)

class wiz_tabs_profile_select(osv.osv_memory):
    _name = 'eagle.wiz_tabs_profile_select'
    _description = 'Eagle wizard: select a tabs profile'

    # ------------------------- Fields related
    
    _columns = {
        'tabs_prof_id': fields.many2one('eagle.config.tabs_profile', 'Select your tabs profile (let empty to use the default one)'),
    }
    
    def _get_current_tabs_profile(self, cr, uid, context={}):
        if context is None: context={}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.eagle_tabs_profile:
            return user.eagle_tabs_profile.id

        params_obj = self.pool.get( 'eagle.config.params' )
        for params in params_obj.browse( cr, uid, params_obj.search( cr, uid, [], context=context ), context=context ):
            if params.tabs_profile:
                return params.tabs_profile.id
        
        return False
    
    _defaults = {
        'tabs_prof_id': _get_current_tabs_profile,
    }
    
    # ---------- Interface related
    
    def do_save(self, cr, uid, ids, context={}):
        datas = self.browse(cr, uid, ids[0], context=context)
        tabs_prod_id = datas.tabs_prof_id and datas.tabs_prof_id.id or False
        self.pool.get('res.users').write(cr, uid, [uid], {'eagle_tabs_profile': tabs_prod_id}, context=context)
        return {}
        
wiz_tabs_profile_select()
