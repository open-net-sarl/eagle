# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_edoctree
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
    'name' : 'Eagle View: eDocTree module',
    'version' : '7.02.05',
    'website': 'http://www.opennet.ch',
    'author' : 'Open Net/Cyp',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'description' : """
Open Net Eagle View System: eDocTree module
-------------------------------------------

This module increases your productivity by introducing a complete hierarchical document management.

**Author :** Open Net Sàrl   Industrie 59  1030 Bussigny  Suisse  http://www.open-net.ch

**Contact :** info@open-net.ch

**History :**

V1.0: 2013-07
    - Linking the eDocTree maangement to Eagle

V7.0: 2013-08-20/Cyp
    - Official version number, according to OpenERP server's version

V7.01: 2013-12-22/Cyp
    - The module also depends on Eagle Meta
    - Better integration in Eagle:
        - at meta creation, copy of an aDocTree template node (based upon config)
        - at contract creation, copy of an aDocTree template node (based upon config)

V7.02.05: 2014-01-07/Cyp
    - Ability to move an eDocTree from its current position to one of the corresponding contract's sub nodes
""",
    'website': 'http://www.open-net.ch',
    'images' : [],
    'depends' : ['eagle_base','eagle_meta','ons_productivity_edoctree'],
    'data': [
    	'wizard/wiz_move_to_view.xml',
        'contracts_view.xml',
    	'edoctree_view.xml',
    	'metas_view.xml',
        'config/res_config_view.xml',
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
    'application': False,
    'auto_install': False,
}
