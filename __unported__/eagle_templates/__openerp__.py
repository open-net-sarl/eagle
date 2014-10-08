# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_templates
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2013 Open-Net Ltd. All rights reserved.
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
	'name': 'Eagle View, templating module',
	'version': '7.02.05',
	'category': 'Eagle view',
	'description': """
Open Net Eagle View System: Templating module
---------------------------------------------

This is the templating module of the Eagle View management system.

**Features list :**
	- task templates: they are added automatically at projects creation (in the frame of an Eagle Contract) or manually
	- contract templates, managed through the meta contract

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**

V1.0:    2013-08-04
    - Scratch writing the contract templating
    - Moving the task templating from Eagl Project to this module

V7.0:    2013-08-20/Cyp
    - Official version number, according to OpenERP server's version

V7.01.02: 2013-12-16/Cyp
    - Depends on the contract states

V7.02.02: 2014-01-23/Cyp
    - New wizard: fill a contract with a template's positions

V7.02.04: 2014-01-28/Cyp
    - The "Use Template" wizard also copies one of the poroduct's description fields in the position's notes field, depending on Eagle's configuration

V7.02.05: 2014-02-17/Cyp
    - Task template button moved in the "Project tasks" tab
    - "Use a template" button moved on the top right of the contract form
	""",
	'author': 'cyp@open-net.ch',
	'website': 'http://www.open-net.ch',
	'depends': ['eagle_base','eagle_project'],
	'init_xml': [],
	'update_xml': [
    	'config/security/ir.model.access.csv',
        'wizard/setup_contract_view.xml',
		'projects_view.xml',
		'contracts_view.xml',
        'config/__menu__.xml',
	],
	'demo_xml': [], 
	'test': [],
	'installable': True,
    'application': True,
	'active': False,
}
