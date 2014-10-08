# -*- coding: utf-8 -*-
#
#  File: config.py
#  Module: eagle_invoice
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

import netsvc
from osv import fields, osv

class eagle_config_params( osv.osv ):
    _inherit = 'eagle.config.params'
    
    _columns = {
        'make_inv_lines_with_unbillables': fields.boolean( 'Unbillable items make invoice lines' ),
        'invoicing_mode': fields.selection( [
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
            ('disabled','Disabled')], 'Invoicing mode',
            help="Automatic and manual have the 'Make Invoice' button visible, disabled no" ),
        'inv_close_cnt_if_inv_payed': fields.boolean( 'May close a contract only if all invoices are paid' ),
        'use_prec_invoices': fields.boolean('Deduct the current invoices', help='Only those tied to the current contract'),
    }
    
    _defaults = {
        'make_inv_lines_with_unbillables': lambda *a: True, 
        'invoicing_mode': lambda *a: 'auto', 
    }

eagle_config_params()

class eagle_config_settings(osv.osv):
    _inherit = 'eagle.config.settings'

    # ---------- Fields management

    _columns = {
        'make_inv_lines_with_unbillables': fields.boolean( 'Unbillable items make invoice lines' ),
        'invoicing_mode': fields.selection( [
            ('auto', 'Automatic'),
            ('manual', 'Manual'),
            ('disabled','Disabled')], 'Invoicing mode',
            help="Automatic and manual have the 'Make Invoice' button visible, disabled no" ),
        'inv_close_cnt_if_inv_payed': fields.boolean( 'May close a contract only if all invoices are paid',
            help="Controlled by 'Eagle Invoice'" ),
        'use_prec_invoices': fields.boolean('Deduct the current invoices', help='Only those tied to the current contract'),
    }

    _defaults = {
        'make_inv_lines_with_unbillables': lambda *a: True,
        'invoicing_mode': lambda *a: 'auto', 
        'inv_close_cnt_if_inv_payed': lambda *a: False,
        'use_prec_invoices': lambda *a: False,
    }

eagle_config_settings()
