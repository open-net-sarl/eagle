# -*- coding: utf-8 -*-
#
#  File: models/sale_subscriptions.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
        return name

    @api.model
    def _default_date_start(self):
        date = datetime.now()
        if self._context.get('default_eagle_contract', False):
            contract = self.env['eagle.contract'].browse(self._context['default_eagle_contract'])
            if contract:
                date = contract.date_start
        return date

    @api.model
    def _default_date(self):
        date = ''
        if self._context.get('default_eagle_contract', False):
            contract = self.env['eagle.contract'].browse(self._context['default_eagle_contract'])
            if contract:
                date = contract.date_end
        return date

    @api.model
    def _default_analytic_account(self):
        analiytic_acc = ''
        if self._context.get('default_eagle_contract', False):
            contract = self.env['eagle.contract'].browse(self._context['default_eagle_contract'])
            if contract:
                analiytic_acc = contract.default_analytic_acc
        return analiytic_acc

    @api.multi
    def _compute_sale_subscr_name(self):
        for subs in self:
            subs.name = subs.name or subs.analytic_account_id.name or _('New')

    sale_subscr_name = fields.Char(string='Subscription Name', compute='_compute_sale_subscr_name', readonly=False, store=True, default=_default_sale_subscr_name)
    eagle_contract = fields.Many2one(comodel_name='eagle.contract', string='File')
    code = fields.Char(default="New")
    date_start = fields.Date(default=_default_date_start)
    date = fields.Date(default=_default_date)
    analytic_account_id = fields.Many2one(default=_default_analytic_account)

    # ---------- Instances management

    @api.multi
    def _update_sale_subscr_line(self, eagle_contract_id):
        SaleSubscriptionLines = self.env['sale.subscription.line']
        line = SaleSubscriptionLines.search([('analytic_account_id', '=', self.id)])
        if len(line):
            line.write({'eagle_contract':eagle_contract_id})

    @api.model
    def create(self, vals):
        do_it = ('eagle_contract' in vals)
        contract = False
        contract_id = vals.get('eagle_contract', False)
        if contract_id:
            contract = self.env['eagle.contract'].browse(contract_id)

        if not vals.get('analytic_account_id', False) and vals.get('sale_subscr_name', False):
            vals['name'] = vals['sale_subscr_name']

        if not vals.get('code', False):
            vals['code'] = self.env['ir.sequence'].next_by_code('sale.subscription') or 'New'
        if vals.get('name', 'New') == 'New':
            s = ''
            if contract:
                s = contract.name + '/'
                vals['name'] = s + vals['code']

        new_id = super(SaleSubscription, self).create(vals)

        if do_it:
            new_id._update_sale_subscr_line(contract_id)

        return new_id

    @api.multi
    def write(self, vals):
        prefix = ''
        do_it = ('eagle_contract' in vals)
        for subs in self:
            if do_it:
                contract_id = vals.get('eagle_contract', False)
                contract = subs.env['eagle.contract'].browse(contract_id)
                if contract and contract.name:
                    prefix = contract.name + '/'

            ret = super(SaleSubscription, subs).write(vals)

            if do_it:
                subs._update_sale_subscr_line(contract_id)

            if prefix:
                _logger.info("CODE: %s" % subs.code)
                super(SaleSubscription, subs).write({'name': prefix + subs.code})

        return ret

    # ---------- Utils

    @api.multi
    def _prepare_sale_line(self, line, fiscal_position):
        sale_line = super(SaleSubscription, self)._prepare_sale_line(line, fiscal_position)
        sale_line['contract_id'] = line.eagle_contract and line.eagle_contract.id or False
        return sale_line

    @api.multi
    def _prepare_sale_data(self):
        sale = super(SaleSubscription, self)._prepare_sale_data()
        for data in self:
            sale['contract_id'] = data.eagle_contract and data.eagle_contract.id or False
        return sale

    @api.multi
    def _prepare_invoice_line(self, line, fiscal_position):
        invoice_line = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position)
        invoice_line['contract_id'] = line.analytic_account_id and \
                    line.analytic_account_id.eagle_contract and \
                    line.analytic_account_id.eagle_contract.id or False
        return invoice_line

    @api.multi
    def _prepare_invoice_data(self):
        invoice = super(SaleSubscription, self)._prepare_invoice_data()
        for data in self:
            invoice['contract_id'] = data.eagle_contract and data.eagle_contract.id or False
        return invoice

    @api.multi
    def setup_sale_filter(self, contract, filter):
        filter = super(SaleSubscription, self).setup_sale_filter(contract, filter)
        if contract and contract.eagle_contract:
            filter.append(('contract_id', '=', contract.eagle_contract.id))
        return filter

    @api.multi
    def setup_invoice_filter(self, contract, filter):
        filter = super(SaleSubscription, self).setup_invoice_filter(contract, filter)
        if contract and contract.eagle_contract:
            filter.append(('contract_id', '=', contract.eagle_contract.id))
        return filter


    @api.multi
    def action_recurring_invoice(self):

        for row in self:
            if not row.eagle_contract:
                continue
            if row.eagle_contract.state in ['confirm', 'production']:
                continue
            raise UserError(_("As long as the file is not active, you can't generate anything."))

        ret = super(SaleSubscription, self).action_recurring_invoice()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # ---------- Scheduler
    @api.multi
    def _cron_recurring_create_invoice(self):
        return self._recurring_create_invoice()


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.subscription.line'
    _order = 'sequence'

    eagle_contract = fields.Many2one('eagle.contract', string='File')
    eagle_note = fields.Text(string="Note")

    @api.model
    def create(self, vals):
        if vals.get('analytic_account_id', False):
            sale_sub = self.env['sale.subscription'].browse(vals['analytic_account_id'])
            if sale_sub and sale_sub.eagle_contract:
                vals['eagle_contract'] = sale_sub.eagle_contract.id

        return super(SaleSubscriptionLine, self).create(vals)

    # ---------- UI management
    @api.onchange('quantity')
    def onchange_product_qty(self):
        _logger.info("ONCHANGE QTY")
        _logger.info(self._context)
        for subs in self:
            description = subs.name

            res = super(SaleSubscriptionLine, subs).onchange_product_id()

            if subs.product_id:
                if 'value' not in res:
                    res['value'] = {}

                res['value'].update({
                    'name': description
                    })
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        _logger.info("ONCHANGE")
        _logger.info(self._context)
        for subs in self:
            res = super(SaleSubscriptionLine, subs).onchange_product_id()
            contract = subs.analytic_account_id
            company_id = contract.company_id.id
            pricelist_id = contract.pricelist_id.id

            if subs.product_id:
                if 'value' not in res:
                    res['value'] = {}
                ctx = dict(subs.env.context, company_id=company_id, force_company=company_id, pricelist=pricelist_id, quantity=subs.quantity)

                prod = subs.env['product.product'].with_context(ctx).browse(subs.product_id.id)
                if prod.recurring_rule_type and prod.recurring_interval:
                    next_date = datetime.now()
                    failed = True
                    if prod.recurring_rule_type == 'daily':
                        next_date += relativedelta(days=prod.recurring_interval or 1)
                        failed = False
                    elif prod.recurring_rule_type == 'weekly':
                        next_date += relativedelta(days=7*(prod.recurring_interval or 1))
                        failed = False
                    elif prod.recurring_rule_type == 'monthly':
                        next_date += relativedelta(months=prod.recurring_interval or 1)
                        failed = False
                    elif prod.recurring_rule_type == 'yearly':
                        next_date += relativedelta(years=prod.recurring_interval or 1)
                        failed = False
                    if failed:
                        res['value'].update({
                            'recurring_rule_type': 'none',
                            'recurring_interval': 1,
                            'recurring_next_date': None
                        })
                    else:
                        res['value'].update({
                            'recurring_rule_type': prod.recurring_rule_type,
                            'recurring_interval': prod.recurring_interval,
                            'recurring_next_date': next_date
                        })

        return res
