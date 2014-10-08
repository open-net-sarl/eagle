# -*- coding: utf-8 -*-
#
#  File: moves.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2012 Open-Net Ltd. All rights reserved.
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

class account_move( osv.osv ):
    _inherit = 'account.move'
    
    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)
        ml_obj = self.pool.get('account.move.line')
        inv_obj = self.pool.get('account.invoice')

        if not valid_moves:
            raise osv.except_osv(_('Integrity Error !'), _('You cannot validate a non-balanced entry !\nMake sure you have configured Payment Term properly !\nIt should contain atleast one Payment Term Line with type "Balance" !'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name =='/':
                new_name = False
                journal = move.journal_id
                
                invoice = False
                mv = self.read(cr, uid, move.id, context=context)
                for ml in ml_obj.read(cr, uid, mv['line_id'], context=context ):
                    if ml.get('invoice'):
                        invoice = inv_obj.browse(cr, uid, ml['invoice'][0], context=context)
                        if invoice and invoice.contract_id:
                            context.update({'contract_id': invoice.contract_id.id})
                            break

                if invoice:
                    if invoice.name:
                        new_name = invoice.name
                    elif invoice.origin:
                       new_name = invoice.origin
                    elif invoice.internal_number:
                        new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        if context.get('contract_id', False):
                            c.update({'contract_id':context['contract_id']})
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, context=c)
                    else:
                        raise osv.except_osv(_('Error'), _('No sequence defined on the journal !'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})

        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))

        return True

account_move()
