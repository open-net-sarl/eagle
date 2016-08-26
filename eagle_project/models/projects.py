# -*- coding: utf-8 -*-
#
#  File: models/projects.py
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. All rights reserved.


from openerp import fields, models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    eagle_contract = fields.Many2one('eagle.contract', string='File')


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.onchange
    @api.v8
    def onchange_project(self):
        ret = super(ProjectIssue, self).on_change_project()
        if not (ret or {}).get('value'):
            return ret

        for field in ['partner_id', 'email_from']:
            if ret['value'].get(field):
                del ret['value'][field]

        return ret

    @api.v7
    def on_change_project(self, cr, uid, ids, project_id, context=None):
        ret = super(ProjectIssue, self).on_change_project(cr, uid, ids, project_id, context=context)
        if not (ret or {}).get('value'):
            return ret

        for field in ['partner_id', 'email_from']:
            if ret['value'].get(field):
                del ret['value'][field]

        return ret

