# -*- coding: utf-8 -*-
#
#  File: base.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2012 Open-Net Ltd. All rights reserved.
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

import netsvc
from osv import fields, osv
import time

class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'

    def _interpolate(self, s, d, context=None):
        if context is None:
            context = {}
        if s:
            if '(eagle_contract)' in s:
                contract_name = ''
                contract_id = context.get('contract_id', False)
                if contract_id:
                    contract = self.pool.get('eagle.contract').read(cr, uid, [context['contract_id']], ['name'], context=context )
                    if contract and contract[0].get('name'):
                        contract_name = contract[0]['name']
                d.update({'eagle_contract':contract_name})

            return s % d
        return  ''

    def _next(self, cr, uid, seq_ids, context=None):
        if not seq_ids:
            return False
        if context is None:
            context = {}

        for seq in self.browse(cr, uid, seq_ids, context):
            for line in seq.fiscal_ids:
                if line.fiscalyear_id.id == context.get('fiscalyear_id'):
                    seq_ids = [line.sequence_id.id]
                    break

        force_company = context.get('force_company')
        if not force_company:
            force_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        sequences = self.read(cr, uid, seq_ids, ['company_id','implementation','number_next','prefix','suffix','padding'])
        preferred_sequences = [s for s in sequences if s['company_id'] and s['company_id'][0] == force_company ]
        seq = preferred_sequences[0] if preferred_sequences else sequences[0]
        if seq['implementation'] == 'standard':
            cr.execute("SELECT nextval('ir_sequence_%03d')" % seq['id'])
            seq['number_next'] = cr.fetchone()
        else:
            cr.execute("SELECT number_next FROM ir_sequence WHERE id=%s FOR UPDATE NOWAIT", (seq['id'],))
            cr.execute("UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s ", (seq['id'],))

        d = self._interpolation_dict()
        interpolated_prefix = self._interpolate(seq['prefix'], d, context=context)
        interpolated_suffix = self._interpolate(seq['suffix'], d, context=context)

        return interpolated_prefix + '%%0%sd' % seq['padding'] % seq['number_next'] + interpolated_suffix

#     def next_by_id(self, cr, uid, sequence_id, context=None):
#         """ Draw an interpolated string using the specified sequence."""
#         self.check_read(cr, uid)
#         company_ids = self.pool.get('res.company').search(cr, uid, [], order='company_id', context=context) + [False]
#         ids = self.search(cr, uid, ['&',('id','=', sequence_id),('company_id','in',company_ids)])
#         return self._next(cr, uid, ids, context)
# 
#     def next_by_code(self, cr, uid, sequence_code, context=None):
#         """ Draw an interpolated string using a sequence with the requested code.
#             If several sequences with the correct code are available to the user
#             (multi-company cases), the one from the user's current company will
#             be used.
# 
#             :param dict context: context dictionary may contain a
#                 ``force_company`` key with the ID of the company to
#                 use instead of the user's current company for the
#                 sequence selection. A matching sequence for that
#                 specific company will get higher priority. 
#         """
#         self.check_read(cr, uid)
#         company_ids = self.pool.get('res.company').search(cr, uid, [], order='company_id', context=context) + [False]
#         ids = self.search(cr, uid, ['&',('code','=', sequence_code),('company_id','in',company_ids)])
#         return self._next(cr, uid, ids, context)
# 
ir_sequence()
