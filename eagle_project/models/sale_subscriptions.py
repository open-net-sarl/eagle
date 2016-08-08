# -*- coding: utf-8 -*-
#
#  File: models/sale_subscriptions.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.model
    def _default_sale_subscr_name(self):
        name = ''
        if self._context.get('default_eagle_contract', False):
            contract = self.env['eagle.contract'].browse(self._context['default_eagle_contract'])
            if contract:
                name = contract.name
                if contract.default_ssubscr_acc:
                    name += '/' + contract.default_ssubscr_acc.code
        return name

    @api.one
    def _compute_sale_subscr_name(self):
        self.name = self.name or self.analytic_account_id.name or _('New')

    sale_subscr_name = fields.Char(string='Name', index=True, compute='_compute_sale_subscr_name', readonly=False, store=True, default=_default_sale_subscr_name)
    eagle_contract = fields.Many2one('eagle.contract', 'File')

    _defaults = {
        'code': 'New',
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
        contract = False
        contract_id = vals.get('eagle_contract', False)
        if contract_id:
            contract = self.pool.get('eagle.contract').browse(cr, uid, contract_id, context=context)
            if contract.default_ssubscr_acc:
                vals['analytic_account_id'] = contract.default_ssubscr_acc.id
                for subscr in contract.sale_subscriptions:
                    vals.update({
                        'code': subscr.code,
                        'name': subscr.name
                    })
                    break
        if vals.get('type', 'template') == 'contract' and not vals.get('analytic_account_id', False):
            vals['name'] = vals['sale_subscr_name']

        if not vals.get('code', False):
            vals['code'] = self.pool['ir.sequence'].next_by_code(cr, uid, 'sale.subscription', context=context) or 'New'
        if vals.get('name', 'New') == 'New':
            s = ''
            if contract:
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

    # ---------- Scheduler

    def _cron_recurring_create_invoice(self, cr, uid, context=None):
        return self._recurring_create_invoice(cr, uid, [], automatic=True, context=context)


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'

    eagle_contract = fields.Many2one('eagle.contract', string='File')
    eagle_note = fields.Text(string="Note")

    def create(self, cr, uid, vals, context=None):
        if vals.get('analytic_account_id', False):
            sale_sub = self.pool['sale.subscription'].browse(cr, uid, vals['analytic_account_id'], context=context)
            if sale_sub and sale_sub.eagle_contract:
                vals['eagle_contract'] = sale_sub.eagle_contract.id

        return super(SaleSubscriptionLine, self).create(cr, uid, vals, context=context)

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # ---------- Fields management

    @api.model
    def _default_analytic_account_code(self):
        code = ''
        if self._context.get('default_eagle_contract', False):
            contract = self.env['eagle.contract'].browse(self._context['default_eagle_contract'])
            if contract and contract.default_ssubscr_acc:
                for subscr in contract.sale_subscriptions:
                    code = subscr.code
                    break
        if not code:
            code = self.env['ir.sequence'].next_by_code('sale.subscription') or 'New'

        return code

    code = fields.Char(string='Reference', index=True, track_visibility='onchange', default=_default_analytic_account_code)

    # ---------- Interface management

    def subscriptions_action(self, cr, uid, ids, context=None):
        accounts = self.browse(cr, uid, ids, context=context)
        subscription_ids = sum([account.subscription_ids.ids for account in accounts], [])
        result = {
            "type": "ir.actions.act_window",
            "res_model": "sale.subscription",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", subscription_ids]],
            "context": {"create": False},
            "name": "Subscriptions",
        }
        if len(subscription_ids) == 1:
            result['views'] = [(False, "form")]
            result['res_id'] = subscription_ids[0]

        return result

