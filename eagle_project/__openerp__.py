# -*- coding: utf-8 -*-
#
#  File: __openerp__.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011-TODAY Open-Net Ltd. <http://www.open-net.ch>
{
    'name' : 'Eagle View: project module',
    'version' : '9.1.03',
    'author' : 'Open Net/Cyp',
    'category': 'Eagle view',
    'summary': 'Synthetic view on your business',
    'website': 'http://www.open-net.ch',
    'depends' : [
        'eagle_base',
        'analytic',
        'account',
        'project_issue_sheet',
        'sale_service',
        'sale_stock',
        'sale_order_dates',
        'ons_productivity_sol_req',
        'ons_productivity_subscriptions_adv'
    ],
    'data': [
    	'config/views/view_config.xml',
    	'views/view_invoices.xml',
		'views/view_contracts.xml',
        'views/view_sales.xml',
        'config/menu_items.xml',
        'views/view_sale_subscription.xml',
        'views/view_projects.xml',
        'views/view_crm.xml',
        'views/view_products.xml'
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
    'installable': False,
    'application': True,
    'auto_install': False,
}
