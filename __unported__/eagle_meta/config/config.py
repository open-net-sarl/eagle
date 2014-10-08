# -*- coding: utf-8 -*-
#
#  File: config/config.py
#  Module: eagle_meta
#  Eagle's config management
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)

class eagle_config_params( osv.osv ):
    _inherit = 'eagle.config.params'
    
    # ---------- Fields management

    _columns = {
        'meta_mandatory': fields.boolean('Meta is mandatory', help='If True, the contract must be linked to a meta-contract.'),
        'use_meta_seq': fields.boolean('Use the meta-contract sequence'),
        'use_meta_4_name': fields.boolean('Inherit the name from the meta-contract'),
        'use_meta_4_name_digits': fields.integer('Number of digits'),
    }
    
    _defaults = {
        'meta_mandatory': lambda *a: False,
        'use_meta_seq': lambda *a: False,
        'use_meta_4_name': lambda *a: False,
        'use_meta_4_name_digits': lambda *a: 3,
    }

eagle_config_params()

class eagle_config_settings(osv.osv):
    _inherit = 'eagle.config.settings'

    # ---------- Fields management

    _columns = {
        'meta_mandatory': fields.boolean( 'Meta is mandatory', help='If True, the contract must be linked to a meta-contract.' ),
        'use_meta_seq': fields.boolean('Use the meta-contract sequence'),
        'use_meta_4_name': fields.boolean( 'Inherit the name from the meta-contract / nb. digits' ),
        'use_meta_4_name_digits': fields.integer('Number of digits'),
    }

    _defaults = {
        'meta_mandatory': lambda *a: False,
        'use_meta_seq': lambda *a: False,
        'use_meta_4_name': lambda *a: False,
        'use_meta_4_name_digits': lambda *a: 3,
    }

eagle_config_settings()
 
