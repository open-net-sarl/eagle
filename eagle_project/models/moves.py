# -*- coding: utf-8 -*-
#
#  File: models/moves.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>
##############################################################################

from openerp import models, fields, api
from openerp.exceptions import except_orm

import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def create_analytic_lines(self):
        return super(AccountMoveLine, self).create_analytic_lines()

    @api.multi
    def create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic account. This
            method first remove any existing analytic item related to the line before creating any new one.
        """
        for obj_line in self:
            if obj_line.analytic_account_id:
                if obj_line.analytic_line_ids:
                    obj_line.analytic_line_ids.unlink()
                vals_line = obj_line._prepare_analytic_line()[0]
                self.pool.get('account.analytic.line').create(self._cr, self._uid, vals_line, context=self._context)

    class AccountMove(models.Model):
        _inherit = 'account.move'

    @api.multi
    def post_it(self):
        invoice = self._context.get('invoice', False)
        self._post_validate()

        for move in self:
            move.line_ids.create_analytic_lines()
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            sequence = journal.refund_sequence_id
                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name
        return self.write({'state': 'posted'})

    @api.multi
    def post(self):
        for move in self:
            if move.name != '/':
                continue
            
            ctx = {}
            invoice = False
            for ml in move.line_ids:
                invoice = ml.invoice_id
                if not invoice:
                    continue
                if invoice.contract_id:
                    ctx.update({'contract_id': invoice.contract_id.id})
                    break

            new_name = False
            if invoice and invoice.move_name and invoice.move_name != '/':
                new_name = invoice.move_name
            if not new_name or new_name == '/':
                if ctx:
                    return move.with_context(ctx).post_it()
                else:
                    return move.post_it()
            else:
                self._post_validate()
                move.write({'state': 'posted'})

        return True

