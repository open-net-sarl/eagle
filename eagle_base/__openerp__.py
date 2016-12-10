# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>
##############################################################################
#
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
##############################################################################
{
    'name' : 'Eagle View',
    'version' : '9.6.04',
    'author' : 'Open Net Sàrl',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'website': 'http://www.open-net.ch',
    'depends' : [
        'base',
        'decimal_precision',
        'mail',
        'report',
        'product',
    ],
    'data': [
        'views/eagle_base.xml',
        'config/security/eagle_security.xml',
        'config/security/ir.model.access.csv',
        'config/data/sequences.xml',
        'config/views/view_config.xml',
        'config/wizard/view_tabs_profile_select.xml',
        'config/wizard/view_tabs_profile.xml',
        'config/views/view_tab_profiles.xml',
        'views/view_base.xml',
        'views/view_products.xml',
        'views/view_partners.xml',
        'views/view_contracts.xml',
        'config/menu_items.xml',
        'views/view_users.xml',
    ],
    'qweb' : [
    ],
    'css':[
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
