# -*- coding: utf-8 -*-
#
#  File: config.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

import netsvc
from osv import fields, osv

VISIBILITY_OPTIONS = [('public', 'All Users'),
                ('employees', 'Employees Only'),
                ('followers', 'Followers Only')]

class eagle_config_params( osv.osv ):
	_inherit = 'eagle.config.params'

	_columns = {
		'set_company': fields.boolean( 'Force the company at project creation' ),
		'use_one_project': fields.boolean( 'Use only one project' ),
        'project_privacy_visibility': fields.selection(VISIBILITY_OPTIONS, 'Projects privacy / visibility'),
	}
	
	_defaults = {
		'set_company': lambda *a: False, 
		'use_one_project': lambda *a: False,
        'project_privacy_visibility': lambda *a: 'employees',
	}

eagle_config_params()

class eagle_config_settings(osv.osv):
    _inherit = 'eagle.config.settings'

    # ---------- Fields management

    _columns = {
		'set_company': fields.boolean( "Set the project's company", help="If True, at creation time each project inherits of the contract's company" ),
		'use_one_project': fields.boolean( 'Use only one project' ),
        'project_privacy_visibility': fields.selection(VISIBILITY_OPTIONS, 'Projects privacy / visibility'),
    }

    _defaults = {
        'set_company': lambda *a: False,
		'use_one_project': lambda *a: False, 
        'project_privacy_visibility': lambda *a: 'employees',
    }

eagle_config_settings()
