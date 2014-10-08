# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_crm
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014 Open-Net Ltd. All rights reserved.
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
    'name' : 'Eagle View: CRM module',
    'version' : '7.2.18',
    'website': 'http://www.opennet.ch',
    'author' : 'Open Net/Cyp',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'description' : """
Open Net Eagle View System: CRM module
--------------------------------------

This module increases your productivity by introducing a complete contracts management.

**Features list :**
    - At the time an opportunity is converted into a quotation, you can create a new contract, or you may link to an existing one. In both cases, the sale is linked to the corresponding analytic account.
    - A new tab in a contract: a way to manage messages, meetings and phone calls for each partner in a contract

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**

V7.0: 2013-08-20/Cyp
    - First official version number for OE7, according to OpenERP server's version

V7.1.03: 2014-02-26/Cyp
    - CRM tab

V7.1.04: 2014-03-06/Cyp
    - Eagle contract messages removed, conflict with OE's own messaging system

V7.2.08 2014-03-31/Cyp
    - Introducing the planned revenue and its probability

V7.2.13 2014-04-15/Cyp
    - Introducing back and forth links between leads (opportunites) and contracts, including a wizard
    - Opportunities may handle another currency

V7.2.14 2014-05-20/Cyp
    - List & edit messages for Eagle CRM objects

V7.2.15 2014-06-03/Cyp
    - Nasty bug corrected: now CRM object can be added directly from the Eagle contract CRM tab

V7.2.18 2014-06-17/Cyp
    - Automatic and manual reminder management
""",
    'website': 'http://www.open-net.ch',
    'images' : [],
    'depends' : ['eagle_base', 'eagle_project', 'crm', 'sale_crm', 'web_kanban'],
    'data': [
        'config/security/ir.model.access.csv',
        'wizard/crm_leads_to_contracts_view.xml',
        'config/config_view.xml',
        'crm_view.xml',
        'contracts_view.xml',
        'partners_view.xml',
        'leads_view.xml',
    ],
    'js': [
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
