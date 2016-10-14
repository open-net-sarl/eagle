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
    'version' : '9.2.02',
    'author' : 'Open Net Sàrl',
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
        'sale_timesheet',
        'ons_productivity_sol_req',
        'ons_productivity_subscriptions_adv',
        'account_asset',
        'sale_contract_asset'
    ],
    'data': [
    	'config/views/view_config.xml',
    	'views/view_invoices.xml',
		'views/view_contracts.xml',
        'views/view_sales.xml',
        'views/view_sale_subscription.xml',
        'views/view_projects.xml',
        'views/view_crm.xml',
        'views/view_products.xml',
        'config/menu_items.xml'
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
