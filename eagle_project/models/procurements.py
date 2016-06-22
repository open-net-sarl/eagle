# -*- coding: utf-8 -*-
#
#  File: models/procurements.py
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. All rights reserved.


from openerp import fields, models, api

class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    eagle_contract = fields.Many2one('eagle.contract', string='File')

    @api.v7
    def _run(self, cr, uid, procurement, context=None):
        return super(ProcurementOrder, self)._run(cr, uid, procurement, context=context)

    @api.v8
    def _run(self):
        return super(ProcurementOrder, self)._run()

    @api.v7
    def _create_service_task(self, cr, uid, procurement, context=None):
        new_task_id = super(ProcurementOrder, self)._create_service_task(cr, uid, procurement, context=context)
        if new_task_id:
            self.pool.get('project.task').write(cr, uid, [new_task_id], {'eagle_contract': procurement.eagle_contract.id or False}, context=context)

        return new_task_id

    @api.v8
    def _create_service_task(self):
        new_task = super(ProcurementOrder, self)._create_service_task()
        if new_task:
            new_task.eagle_contract = procurement.eagle_contract or False

        return new_task

