# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_invoice
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
    'name': 'Eagle View, invoices module',
    'version': '7.03.02',
    'category': 'Eagle view',
    'description': """
Open Net Eagle View System: Invoices module
-------------------------------------------

**Features list :**
	- your invoice lines appear in the contract's view, in two tabs:
		- current invoice lines, in draft state
		- past invoice lines, in opened/closed state

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**

V5.0:    2013-07
    - Upgrade to OpenERP 7.0 implementation

V5.0.03: 2013-08-19
    - Moving the invoice management from the 'Eagle Invoice' module to the 'Eagle Project' module
      This is to avoid a duplicate handling with 'Eagle Management'

V7.0:    2013-08-20/Cyp
    - Official version number, according to OpenERP server's version

V7.01: 2013-12-16/Cyp
    - Depends on the contract states

V7.02.02: 2014-01-30/Cyp
    - Invoice line rate
    - In a contrat's form, the invoice lines are readonly from now on, as it some modifications involve some information from the corresponding invoice object 

V7.02.03: 2014-02-17/Cyp
    - "Make Invoice" button moved in the Content tab

V7.02.05: 2014-03-06/Cyp
    - Eagle contract messages removed, conflict with OE's own messaging system

V7.02.06: 2014-03-26/Cyp
    - Cosmetic in the config view

V7.03.02: 2014-03-26/Cyp
    - Handling the customer's fiscal position in the invoices
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_project'],
    'init_xml': [],
    'update_xml': [
    	'contracts_view.xml',
    	'invoices_view.xml',
    	'config/config_view.xml',
    	'wizard/wiz_inv_scheduler.xml',
	],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'application': True,
    'active': False,
}

