# -*- coding: utf-8 -*-
#
#  File: config/events.py
#  Module: eagle_base
#  Eagle's Events management (those linked to the changes of state)
#
#  Created by cyp@open-net.ch
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

import logging
_logger = logging.getLogger(__name__)

import openerp
from openerp.osv import fields, osv

class eagle_config_event_base( osv.osv ):
    _name = 'eagle.config.event'
    _description = 'Eagle Events management'
    _order = 'name'

    # ---------- Fields management

    _columns = {
        'name': fields.selection( [
            ('draft', 'Draft'),
            ('conf', 'Confirmation'),
            ('inst', 'Installation'),
            ('prod', 'Production'),
            ('closed', 'Closed'),
            ('canceled', 'Canceled'),
            ], 'Linked to', required=True ),
    }
    
    _defaults = {
        'name': lambda *a:'draft',
    }
    
    def get_name_by_state(self, cr, uid, ids, state, context={}):
        return {
            'draft': 'draft',    
            'confirm': 'conf',     
            'installation': 'inst',     
            'production': 'prod',     
            'closed': 'closed',   
            'canceled': 'canceled', 
        }.get(state, False)
    
eagle_config_event_base()

class eagle_config_event_line( osv.osv ):
    """each represents a function to call for a contract state change"""

    _name = 'eagle.config.event.line'
    _description = "Eagle event's line"
    
    _order = 'seq,id'

    # ---------- Fields management

    _columns = {
        'name': fields.many2one( 'eagle.config.event', string="Event's name" ),
        'seq': fields.integer( 'Pos' ),
        'function_name': fields.char( 'Function name', size=100 ),
        'module_descr': fields.char( 'Module', size=64 ),
    }
    
    _defaults = {
        'seq': lambda *a:0,
    }
    

eagle_config_event_line()

class eagle_config_event( osv.osv ):
    _inherit = 'eagle.config.event'

    # ---------- Fields management

    def _comp_modules_list(self, cr, uid, events_ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        
        for evt in self.browse(cr, uid, events_ids, context=context):
            res[evt.id] = ', '.join([l.module_descr for l in evt.lines])

        return res

    _columns = {
        'lines': fields.one2many( 'eagle.config.event.line', 'name', 'Lines' ),
        'modules': fields.function(_comp_modules_list, type='char', store=False, string='Modules'),
    }
    
eagle_config_event()
