# -*- coding: utf-8 -*-
#
#  File: models/projects.py
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. All rights reserved.


from openerp import fields, models

class ProjectTask(models.Model):
    _inherit = 'project.task'

    eagle_contract = fields.Many2one('eagle.contract', string='File')

