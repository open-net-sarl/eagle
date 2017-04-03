# -*- coding: utf-8 -*-
#
#  File: models/invoices.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    contract_id = fields.Many2one('eagle.contract', string='File')

    # ---------- Instances management

    @api.multi
    def write(self, vals):
        ret = super(AccountInvoice, self).write(vals)

        if 'contract_id' in vals:
            for invoice in self:
                invoice.invoice_line_ids.write({'contract_id':vals['contract_id']})
        
        return ret

    @api.model
    def create(self, vals):
        new_inv = super(AccountInvoice, self).create(vals)

        if new_inv and vals.get('contract_id', False):
            contract_id = vals['contract_id']
            new_inv.invoice_line_ids.write({'contract_id':contract_id})
        
        return new_inv


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    contract_id = fields.Many2one('eagle.contract', string='File')

