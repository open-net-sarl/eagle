# -*- coding: utf-8 -*-
#
#  File: models/sale_subscriptions.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class SaleSubscription(osv.osv):
    _inherit = 'sale.subscription'

    _columns = {
        'eagle_contract': fields.many2one('eagle.contract', 'File')
    }

    # ---------- Instances management

    def _update_sale_subscr_line(self, cr, uid, ids, eagle_contract_id, context={}):
        if not ids:
            return False
        SaleSubscriptionLines = self.pool.get('sale.subscription.line')
        lines = SaleSubscriptionLines.search(cr, uid, [('analytic_account_id', 'in', ids)], context=context)
        if not lines:
            return False
        SaleSubscriptionLines.write(cr, uid, lines, {'eagle_contract':eagle_contract_id}, context=context)

        return True

    def create(self, cr, uid, vals, context={}):
        do_it = ('eagle_contract' in vals)
        contract_id = vals.get('eagle_contract', False)

        if not vals.get('code', False):
            vals['code'] = self.pool['ir.sequence'].next_by_code(cr, uid, 'sale.subscription', context=context) or 'New'
        if vals.get('name', 'New') == 'New':
            s = ''
            if contract_id:
                contract = self.pool.get('eagle.contract').browse(cr, uid, contract_id, context=context)
                s = contract.name + '/'
            vals['name'] = s + vals['code']

        new_id = super(SaleSubscription, self).create(cr, uid, vals, context=context)

        if do_it:
            self._update_sale_subscr_line(cr, uid, [new_id], contract_id, context=context)

        return new_id

    def write(self, cr, uid, ids, vals, context={}):
        do_it = ('eagle_contract' in vals)
        prefix = ''
        if do_it:
		contract_id = vals.get('eagle_contract', False)
		contract = self.pool.get('eagle.contract').browse(cr, uid, contract_id, context=context)
		if contract and contract.name:
			prefix = contract.name + '/'

        ret = super(SaleSubscription, self).write(cr, uid, ids, vals, context=context)
        if do_it:
            self._update_sale_subscr_line(cr, uid, ids, contract_id, context=context)
	    if prefix:
		for subs in self.browse(cr, uid, ids, context=context):
			super(SaleSubscription, self).write(cr, uid, [subs.id], {'name': prefix + subs.code}, context=context)

        return ret

    # ---------- Utils

    def _prepare_sale_line(self, cr, uid, contract, line, fiscal_position_id, context={}):
        sale_line = super(SaleSubscription, self)._prepare_sale_line(cr, uid, contract, line, fiscal_position_id, context=context)
        sale_line['contract_id'] = contract.eagle_contract and contract.eagle_contract.id or False

        return sale_line

    def _prepare_sale_data(self, cr, uid, contract, context={}):
        sale = super(SaleSubscription, self)._prepare_sale_data(cr, uid, contract, context=context)
        sale['contract_id'] = contract.eagle_contract and contract.eagle_contract.id or False

        return sale

    def _prepare_invoice_line(self, cr, uid, line, fiscal_position, context={}):
        invoice_line = super(SaleSubscription, self)._prepare_invoice_line(cr, uid, line, fiscal_position, context=context)
        invoice_line['contract_id'] = line.analytic_account_id and \
                    line.analytic_account_id.eagle_contract and \
                    line.analytic_account_id.eagle_contract.id or False

        return invoice_line

    def _prepare_invoice_data(self, cr, uid, contract, context=None):
        invoice = super(SaleSubscription, self)._prepare_invoice_data(cr, uid, contract, context=context)
        invoice['contract_id'] = contract.eagle_contract and contract.eagle_contract.id or False

        return invoice

    def setup_sale_filter(self, cr, uid, contract, filter, context={}):
        filter = super(SaleSubscription, self).setup_sale_filter(cr, uid, contract, filter, context=context)
        if contract and contract.eagle_contract:
            filter.append(('contract_id', '=', contract.eagle_contract.id))

        return filter

    def setup_invoice_filter(self, cr, uid, contract, filter, context={}):
        filter = super(SaleSubscription, self).setup_invoice_filter(cr, uid, contract, filter, context=context)
        if contract and contract.eagle_contract:
            filter.append(('contract_id', '=', contract.eagle_contract.id))

        return filter

    def action_recurring_invoice(self, cr, uid, ids, context=None):

        for row in self.browse(cr, uid, ids, context=context):
            if not row.eagle_contract:
                continue
            if row.eagle_contract.state in ['confirm', 'production']:
                continue
            raise UserError(_("As long as the file is not active, you can't generate anything."))

        ret = super(SaleSubscription, self).action_recurring_invoice(cr, uid, ids, context=context)

        return ret


class SaleSubscriptionLine(osv.osv):
    _inherit = 'sale.subscription.line'

    _columns = {
        'eagle_contract': fields.many2one('eagle.contract', 'File')
    }

