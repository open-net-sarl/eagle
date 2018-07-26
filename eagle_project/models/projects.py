# -*- coding: utf-8 -*-
#
#  File: models/projects.py
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. All rights reserved.


from odoo import fields, models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    eagle_contract = fields.Many2one('eagle.contract', string='File')


# class ProjectIssue(models.Model):
#     _inherit = 'project.issue'
#
#     @api.multi
#     @api.onchange
#     def onchange_project(self):
#         ret = super(ProjectIssue, self).on_change_project()
#         if not (ret or {}).get('value'):
#             return ret
#
#         for field in ['partner_id', 'email_from']:
#             if ret['value'].get(field):
#                 del ret['value'][field]
#
#         return ret
