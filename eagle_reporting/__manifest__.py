# -*- coding: utf-8 -*-
#
#  File: __manifest__.py
#  Module: eagle_reporting
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2015-TODAY Open-Net Ltd. <http://www.open-net.ch>
{
    'name' : 'Eagle View: reporting module',
    'version' : '10.0.0.1',
    'website': 'http://www.open-net.ch',
    'author' : 'Open Net Sàrl',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'website': 'http://www.open-net.ch',
    'depends' : [
        'eagle_project',
        'ons_productivity_layout'
    ],
    'data': [
        'views/eagle_reporting.xml',
        'views/report_contracts.xml',
        'views/view_contracts.xml',
        'views/view_sale_subscription.xml'
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
