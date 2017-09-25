# -*- coding: utf-8 -*-
#
#  File: models/partners.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#  MIG[10.0] by lfr@open-net.ch (2017)
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

from collections import OrderedDict
from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class EagleContractPartnerRoleType(models.Model):
    _name = 'eagle.contract.partner_role_type'
    _description = 'Partner role type in an Eagle file'
    
    name = fields.Char('Name', translate=True, required=True)
    type = fields.Selection([
        ('invoice', 'Invoicing'),
        ('delivery', 'Delivery'),
        ('other', 'Other')],
        string='Type',
        required=True)


class EagleContractPartnerRole(models.Model):
    _name = 'eagle.contract.partner_role'
    _description = 'Partner role in an Eagle file'
    
    name = fields.Many2one('eagle.contract.partner_role_type', string='Role type', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    contract_id = fields.Many2one('eagle.contract', string='File', required=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.one
    # @api.depends('name')
    # def _get_comp_name(self):
    #     return dict(self.name_get(self._cr, self._uid, self._ids, context=self._context))

    contract_roles_id = fields.One2many('eagle.contract.partner_role', 'partner_id', string='Roles')
    eagle_contracts = fields.Many2many(
        'eagle.contract', 'eagle_contract_partner_rel', 'partner_id', 'contract_id',
        string='Present in files',
        copy=False)
    # comp_name = fields.Char(compute='_get_comp_name', string='Name')
    eagle_contract_list = fields.One2many('eagle.contract', 'customer_id', compute='_get_eagle_contract_list', string='Files list')
    eagle_contract_count = fields.Integer(compute='_get_eagle_contract_list', string='Files count')

    @api.multi
    def _get_eagle_params(self):
        params = self.env['eagle.contract'].read_eagle_params()

    @api.multi
    def _get_eagle_contract_list(self):
        params = self.env['eagle.contract'].read_eagle_params()
        for part in self:
            res = []
            ref_partner = part.parent_id or part
            p_list = [ref_partner.id] + [p.id for p in ref_partner.child_ids]
            if p_list:
                if len(p_list) == 1:
                    op = '='
                    p_list = p_list[0]
                else:
                    op = 'in'
                filters = [('customer_id', op, p_list)]
                if params.get('use_partners_list', False):
                    filters = ['|'] + filters + [('partners', op, p_list)]
                items = self.env['eagle.contract'].search(filters)
                if items:
                    res = list(OrderedDict.fromkeys([x.id for x in items]))

            part.eagle_contract_list = res
            part.eagle_contract_count = len(res)


class EagleContract(models.Model):
    _inherit = 'eagle.contract'
    
    partner_roles_id = fields.One2many(
        'eagle.contract.partner_role',
        'contract_id',
        string='Partners roles',
        copy=False)

