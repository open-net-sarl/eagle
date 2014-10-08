# -*- coding: utf-8 -*-
#
#  File: crm.py
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

from openerp.osv import fields, osv
from openerp.addons.base_status.base_state import base_state
from tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class eagle_crm( osv.osv ):
    _name = 'eagle.crm'
    _description = 'Eagle CRM object for a contract partner'
    _rec_name = 'partner_id'
    _inherit = ['mail.thread']

    # ---------- Fields management

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade'),
        'contract_id': fields.many2one('eagle.contract', 'Contract'),
		'meeting_ids': fields.one2many('crm.meeting', 'eagle_crm_id', 'Meetings'),
		'phonecall_ids': fields.one2many('crm.phonecall', 'eagle_crm_id', 'Phone calls'),
    }
    
eagle_crm()

class res_partner(osv.osv):
    _inherit = 'res.partner'

    # ---------- Fields management

    _columns = {
        'partner_crm_ids': fields.one2many('eagle.crm', 'partner_id', 'CRM'),
    }

res_partner()

class crm_meeting(osv.Model):
    _inherit = 'crm.meeting'

    # ---------- Fields management

    _columns = {
        'eagle_crm_id': fields.many2one('eagle.crm', 'CRM'),
    }


class crm_phonecall(base_state, osv.osv):
    _inherit = 'crm.phonecall'

    # ---------- Fields management

    _columns = {
        'eagle_crm_id': fields.many2one('eagle.crm', 'CRM'),
    }


class crm_case_stage(osv.osv):
    _inherit = 'crm.case.stage'

    # ---------- Fields management

    _columns = {
        'eagle_state': fields.selection( [
                ( 'draft','Offer' ),
                ( 'confirm','Confirmation' ),
                ( 'installation','Installation' ),
                ( 'production','Production' ),
                ( 'closed','Closed' ),
                ( 'canceled','Canceled' ),
                ], 'Corresp. contract state' ),
    }

