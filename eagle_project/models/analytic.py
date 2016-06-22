# -*- coding: utf-8 -*-
#
#  File: models/analytic.py
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. All rights reserved.


from openerp import api, fields, models

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    eagle_contract = fields.Many2one('eagle.contract', string='File')

    # ---------- Instances management

    @api.v8
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

    @api.v7
    def create(self, cr, uid, vals, context={}):
        new_line_id = super(AccountAnalyticLine, self).create(cr, uid, vals, context=context)

        if not new_line_id:
            return new_line_id
        new_line = self.browse(cr, uid, new_line_id, context=context)

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
            new_line.write({'eagle_contract': eagle_contract.id})

        return new_line_id
