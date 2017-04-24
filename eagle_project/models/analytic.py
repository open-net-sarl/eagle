# -*- coding: utf-8 -*-
#
#  File: models/analytic.py
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. All rights reserved.


from odoo import api, fields, models

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    eagle_contract = fields.Many2one('eagle.contract', string='File')

    # ---------- Instances management

    @api.model
    def create(self, vals):
        new_line = super(AccountAnalyticLine, self).create(vals)

        if not new_line:
            return new_line

        try:
            eagle_contract = new_line.issue_id.task_id.eagle_contract
        except:
            eagle_contract = False

        if not eagle_contract:
            try:
                eagle_contract = new_line.task_id.eagle_contract
            except:
                pass

        if eagle_contract:
            new_line.eagle_contract = eagle_contract

        return new_line

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    eagle_contract_id = fields.One2many(
        'eagle.contract',
        'default_analytic_acc',
        string="Eagle contract ID",
        required=False)


    @api.multi
    def projects_action(self):
        project_ids = sum([account.project_ids.ids for account in self], [])
        result = {
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", project_ids]],
            "context": {"create": False},
            "name": "Projects",
        }
        if len(project_ids) == 1:
            result['views'] = [(False, "form")]
            result['res_id'] = project_ids[0]

        return result

    @api.model
    def _default_analytic_account_code(self):
        code = ''
        if self._context.get('default_eagle_contract', False):
            contract = self.env['eagle.contract'].browse(self._context['default_eagle_contract'])
            if contract:
                for subscr in contract.sale_subscriptions:
                    code = subscr.code
                    break
        if not code:
            code = self.env['ir.sequence'].next_by_code('sale.subscription') or 'New'

        return code

    code = fields.Char(string='Reference', index=True, track_visibility='onchange', default=_default_analytic_account_code)

    

    @api.multi
    def subscriptions_action(self):
        accounts = self
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
