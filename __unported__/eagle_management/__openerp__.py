# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_management
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
    'name': 'Eagle View, management module',
    'version': '7.02.07',
    'category': 'Eagle view',
    'description': """
Open Net Eagle View System: Management module
---------------------------------------------

This is the management module of the Eagle management system.

**Features list :**
    - Sale management: automatic sales and purchases
    - Invoices and analytic entries displayed in the contract view
    - Stock moves, incoming and outgoing products, as well as procurements displayed in the contract view

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**
V4.6.01
    - Profile management

V5.0:   2013-08
    - Upgrade to OpenERP 7.0 implementation

V7.0:   2013-08-20/Cyp
    - Official version number, according to OpenERP server's version

V7.01: 2013-12-16/Cyp
    - Depends on the contract states

V7.02.0: 2014-02-17/Cyp
    - "Make Sale" button moved in the Content tab

V7.02.05: 2014-03-06/Cyp
    - Eagle contract messages removed, conflict with OE's own messaging system

V7.02.06: 2014-03-26/Cyp
    - Cosmetic in the config view

V7.02.07: 2014-08-28/Cyp
    - Unique, coherent functions to set sale's and sale line's default values, while at installation and during production
    - Manages the product's procurement method
    """,
    'author': 'cyp@open-net.ch',
    'website': 'http://www.open-net.ch',
    'depends': ['eagle_project','eagle_base','sale','stock','purchase','mrp'],
    'init_xml': [],
    'update_xml': [
        'sales_view.xml',
        'contracts_view.xml',
        'config/config_view.xml',
        'stock_view.xml',
        'wizard/wiz_mgt_scheduler.xml',
        'wizard/wiz_cust_delivery_date_view.xml',
        'purchases_view.xml',
    ],
    'demo_xml': [], 
    'test': [],
    'installable': True,
    'application': True,
    'active': False,
}

