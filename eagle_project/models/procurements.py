# -*- coding: utf-8 -*-
#
#  File: models/procurements.py
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. All rights reserved.


from odoo import fields, models, api

# class ProcurementOrder(models.Model):
#     _inherit = 'procurement.order'
#
#     eagle_contract = fields.Many2one('eagle.contract', string='File')
#
#     @api.multi
#     def _run(self):
#         return super(ProcurementOrder, self)._run()
#
#     @api.multi
#     def _create_service_task(self):
#         new_task = super(ProcurementOrder, self)._create_service_task()
#         for procurement in self:
#             if new_task:
#                 new_task.eagle_contract = procurement.eagle_contract or False
#         return new_task
#
