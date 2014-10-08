# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
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
{
    'name' : 'Eagle View: base module',
    'version' : '7.11.03',
    'website': 'http://www.opennet.ch',
    'author' : 'Open Net/Cyp',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'description' : """
Open Net Eagle View System: Base module
---------------------------------------

This module increases your productivity by introducing a complete contracts management.

**Features list :**
    - Basic contract position management
    - Product's recurrencies
    - Waranty managment for each contract position
    - Events configuration: As the Eagle Concept is built around a base module and parallel, optionnal modules, 
      this class let us handle parallel events attach to buttons (for example).
    - Tabs profiles management

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**

V5.0: 2013-07
    - Upgrade to OpenERP 7.0 implementation

V5.01: 2013-08-19/Cyp
    - String options list in a tabs profile converted to text (as of today, all options=217/255 chars)

V7.0: 2013-08-20/Cyp
    - Official version number, according to OpenERP server's version

V7.0.14: 2013-11-21/Cyp
    - Improvements with the configuration and the interface
    - Normalization of the structure of the modules
    - Normalization of the versioning of the modules

V7.01.0: 2013-12-16/Cyp
    - Introducing a new state for the contracts: canceled

V7.02.02: 2014-01-06/Cyp
    - Setting up the security for contract categories
    - Main "Contracts" menu: "Current sales" moved on top, "All contracts by customer" moved below "All contracts" (speed)

V7.02.03: 2014-01-10/Cyp
    - Setting up the security for the Eagle events and event lines
    - Bug corrected: position'recurrence and date edition (unknown field 'context_lang')

V7.03.02: 2014-01-12/Cyp
    - Config: select the field during the "on_change_product" event (contract positions)

V7.04.03: 2014-01-15/Cyp
    - Managing roles for the partners

V7.05.07: 2014-01-23/Cyp
    - Contract list: version 7.0
    - Contract positions:
        - new state: progressive (+ float:rate and boolean:invoiced)
        - next action date is managed for all positions
    - Contracts are sorted by start date desc, id desc
    - Parameters: links to Eagle-based views
    - Wizard: rebuild the sequences of the positions

V7.06.0: 2014-01-28/Cyp
    - Custom columns list in contracts positions
    - New wizard: copy the contract's position to another contract

V7.07.0: 2014-02-16/Cyp
    - Eagle contracts now inherit from the messaging system

V7.07.02: 2014-02-17/Cyp
    - Wizard buttons moved from the upper bar down to the right, in a specific DIV

V7.08.04: 2014-03-06/Cyp
    - Eagle contract messages removed, conflict with OE's own messaging system
    - Eagle config param object readable for everybody (causes an error for non-Eagle authorised users)

V7.09.03: 2014-03-09/Cyp
    - Eagle contract may now have a new state: confirmed, between the 'draft' and the 'installation/production' states

V7.10.09: 2014-03-31/Cyp
    - Checkbox to let the user edit the position inline, in the tree
    - Each user may have his/her own setting for the inline position edition

V7.10.11: 2014-04-14/Cyp
    - Partners list of the Eagle contract tab displays also the company's, if any

V7.10.14: 2014-04-15/Cyp
    - Partners list of the Eagle contract tab displays also the company's, if any

V7.10.15: 2014-05-19/Cyp
    - Link between the partner and the contracts includes now that fact it may also be only a customer, not only a participant
    - Number of contracts in the kanban view of the partner
    - List & edit messages for Eagle Contract objects

V7.10.16: 2014-06-20/Cyp
    - The contract in the positions's switched view remains hidden

V7.11.0: 2014-07-10/Cyp
    - Percentage-based discount in positions
    - "Other infos" tabs: "Price(s)" group label changed to "Financial infos"
    - Product units on contract positions

V7.11.03: 2014-08-27/Cyp
    - Products and Product categories menu entries recalled under Contracts > Configuration
    - Procure method reported in the contract's position
""",
    'website': 'http://www.open-net.ch',
    'images' : [],
    'depends' : ['base_setup','product','mrp','web_kanban'],
    'data': [
    	'config/security/eagle_security.xml',
    	'config/security/ir.model.access.csv',
        'config/data/sequences.xml',
        'config/config_view.xml',
        'config/events_view.xml',
        'config/wizard/wiz_tabs_profile_view.xml',
        'config/wizard/wiz_tabs_profile_select_view.xml',
        'config/tab_profiles_view.xml',
        'wizard/wiz_rebuild_pos_seq.xml',
        'wizard/wiz_copy_positions_to.xml',
        'base_view.xml',
    	'products_view.xml',
    	'partners_view.xml',
    	'contracts_view.xml',
	   	'config/__menu_items__.xml',
    	'users_view.xml',
    ],
    'js': [
        'static/src/js/kanban.js'
    ],
    'qweb' : [
    ],
    'css':[
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
