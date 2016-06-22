# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, fields, api



class EagleContract(models.Model):
    _inherit = 'eagle.contract'

    @api.multi
    def migrate_positions(self):
        map_recurrency = {
            'day': 'daily',
            'week': 'weekly',
            'month': 'monthly',
            'year': 'yearly'
        }
        for contract in self: 
            sale_sub_obj = self.env['sale.subscription']
            sale_sub = sale_sub_obj.create({
                'eagle_contract': contract.id,
                'name': 'test'
            })
            for position in self.positions:
                sale_sub_line_obj = self.env['sale.subscription.line']
                sale_sub_line_obj.create({
                    'eagle_contract': contract.id,
                    'analytic_account_id': sale_sub.id,
                    'price_unit': position.list_price,
                    'uom_id': position.uom_id.id,
                    'name': position.description or '',
                    'product_id': position.name.id,
                    'recurring_interval': position.recurrence_id.value,
                    'recurring_rule_type': map_recurrency.get(position.recurrence_id.unit)  or 'none',
                    'requested_date': position.next_invoice_date,
                    'is_billable': position.is_billable,
                    'is_active': position.is_active,
                })


