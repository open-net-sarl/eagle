# -*- coding: utf-8 -*-
#
#  File: __manifest__.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>
##############################################################################
#
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
##############################################################################
{
    'name' : 'Eagle View',
    'version' : '10.0.0.1',
    'author' : 'Open Net Sàrl',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'website': 'http://www.open-net.ch',
    'depends' : [
        'base',
        'decimal_precision',
        'mail',
        'product',
    ],
    'data': [
        'views/eagle_base.xml',
        'security/eagle_security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/view_config.xml',
        'views/view_base.xml',
        'views/view_products.xml',
        'views/view_partners.xml',
        'views/view_contracts.xml',
        'views/menu_items.xml',
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
