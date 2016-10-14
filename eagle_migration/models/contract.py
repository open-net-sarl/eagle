# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, fields, api

#Import logger
import logging
#Get the logger
_logger = logging.getLogger(__name__)

class EagleContract(models.Model):
    _inherit = 'eagle.contract'

    @api.multi
    def migrate_positions(self, template):
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
                'name': 'test',
                'date_start': contract.date_start,
                'template_id': template.id,
                'partner_id': contract.customer_id.id,
                'pricelist_id': template.pricelist_id.id,
                'recurring_generates': template.recurring_generates,

            })
            for position in contract.positions:
                sale_sub_line_obj = self.env['sale.subscription.line']
                sale_sub_line_obj.create({
                    'eagle_contract': contract.id,
                    'analytic_account_id': sale_sub.id,
                    'price_unit': position.list_price,
                    'uom_id': position.uom_id.id or 1,
                    'name': position.description or '',
                    'product_id': position.name.id,
                    'recurring_interval': position.recurrence_id.value,
                    'recurring_rule_type': map_recurrency.get(position.recurrence_id.unit)  or 'none',
                    'recurring_next_date': position.next_invoice_date,
                    'is_billable': position.is_billable,
                    'is_active': position.is_active,
                    'sequence': position.sequence,
                    'cancellation_deadline': position.cancellation_deadline,
                    'discount': position.discount,
                    'sold_quantity': position.qty,
                    'eagle_note': position.notes,
                })


class EagleContract(models.TransientModel):
    _name = 'eagle.contract.migration.wizard'

    eagle_subscription_template = fields.Many2one('sale.subscription', domain="[('type', '=', 'template')]", string="Subscription template")
    
    @api.multi
    def migrate_positions(self):
        active_ids = self._context.get('active_ids', []) or []
        contracts = self.env['eagle.contract'].browse(active_ids)
        contracts.migrate_positions(self.eagle_subscription_template)
