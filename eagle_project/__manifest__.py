# -*- coding: utf-8 -*-
#
#  File: __manifest__.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2011-TODAY Open-Net Ltd. <http://www.open-net.ch>
{
    'name' : 'Eagle View: project module',
    'version' : '10.0.0.2',
    'author' : 'Open Net Sàrl',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'website': 'http://www.open-net.ch',
    'depends' : [
        'eagle_base',
        'analytic',
        'account',
        'hr_timesheet',
        'sale_stock',
        'sale_order_dates',
        'sale_timesheet',
        'ons_productivity_sol_req',
        'ons_productivity_subscriptions_adv',
        'ons_productivity_layout',
        'account_asset',
        'sale_subscription_asset',
        'sale_margin'
    ],
    'data': [
    	'views/view_config.xml',
    	'views/view_invoices.xml',
		'views/view_contracts.xml',
        'views/view_sales.xml',
        'views/view_sale_subscription.xml',
        'views/view_projects.xml',
        'views/view_crm.xml',
        'views/menu_items.xml'
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
