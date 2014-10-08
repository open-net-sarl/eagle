# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
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

{
	'name': 'Eagle View, projects module',
	'version': '7.02.03',
	'category': 'Eagle view',
	'description': """
Open Net Eagle View System: Projects module
-------------------------------------------

This is the projects module of the Eagle View management system

**Features list :**
	- links the contract to the projects:
        - 1 main project
    	- 2 sub-projects: 1 for installation + 1 for production (recurrent items)
	- the main project, the linked tasks, works and analytic items are visible in their respective tabs

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**

V5.0:    2013-07
    - Upgrade to OpenERP 7.0 implementation

V5.0.05: 2013-08-04
    - Moving the task templating from this module to Eagle Templates

V5.0.06: 2013-08-19
    - Moving the invoice management from the 'Eagle Invoice' module to the 'Eagle Project' module
      This is to avoid a duplicate handling with 'Eagle Management'

V7.0: 2013-08-20/Cyp
    - Official version number, according to OpenERP server's version

V7.0.04: 2014-01-15/Cyp
    - Bug corrected: "set_company" setting in Eagle's params

V7.0.05: 2014-01-24/Cyp
    - Bug corrected: better visibility management of the positions' amount and taxes columns

V7.0.06: 2014-02-17/Cyp
    - Project field: minor XML correction, area for buttons on the right

V7.0.02: 2014-03-06/Cyp
    - Eagle contract messages removed, conflict with OE's own messaging system

V7.0.09: 2014-03-26/Cyp
    - Handling contract position switched view
    - Cosmetic in the config view

V7.02.02: 2014-07-10/Cyp
    - Adaptation for the new 'discount' field on contract's positions
    - Fiscal position now handled at the contract level
    - Eagle configuration: "Use only one project" checkbox
    - Project's default visibility, when created by Eagle

V7.02.03: 2014-08-28/Cyp
    - If the corresponding checkbox is set, Eagle will generate one and only one project
	""",
	'author': 'cyp@open-net.ch',
	'website': 'http://www.open-net.ch',
	'depends': ['eagle_base','project','project_mrp','hr','hr_attendance','hr_timesheet_invoice','project_timesheet'],
	'init_xml': [],
	'update_xml': [
    	'config/security/ir.model.access.csv',
    	'config/config_view.xml',
        'projects_view.xml',
    	'invoices_view.xml',
		'contracts_view.xml',
        'config/__menu__.xml',
	],
	'demo_xml': [], 
	'test': [],
	'installable': True,
    'application': True,
	'active': False,
}
