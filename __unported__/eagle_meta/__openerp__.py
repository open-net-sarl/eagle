# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_meta
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
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

{
    'name': 'Eagle View, Meta-contracts module',
    'version': '7.05.07',
    'category': 'Eagle view',
    'description': """
Open Net Eagle View System: Meta-contracts module
-------------------------------------------------

This is the Meta-contract module of the Eagle View management system

**Features list :**
	- regroupement of contracts
	- appointments handled in the meta structure, and visible within the sub-contracts

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**

V5.0: 2013-07
    - Upgrade to OpenERP 7.0 implementation

V7.0: 2013-08-20/Cyp
    - Official version number, according to OpenERP server's version

V7.02: 2013-11-12/Cyp
    - Introducing the configuration for this module
        - Force each contract to be linked to a meta-contract
        - Meta may use its own sequence
        - Linked contract derived their name from their meta-contract 

V7.03: 2013-12-16/Cyp
    - Depends on the contract states

V7.04: 2014-01-06/Cyp
    - Added the Meta field in the search for contracts, and in their list

V7.05.06: 2014-01-23/Cyp
    - When a meta is mandatory for contracts, can't create new contract or add contracts to a meta outside the template wizard
    - Meta are sorted by id desc

V7.05.07: 2014-03-26/Cyp
    - Cosmetic in the config view
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_base'],
    'init_xml': [],
    'update_xml': [
    	'config/security/ir.model.access.csv',
        'config/data/sequences.xml',
        'config/config_view.xml',
        'wizard/add_contracts_view.xml',
    	'contracts_view.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'application': True,
    'active': False,
}
