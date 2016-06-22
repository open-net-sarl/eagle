# -*- coding: utf-8 -*-
#
#  File: models/partners.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

from collections import OrderedDict
import re

from openerp import _, api, fields, models

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

    @api.one
    def _default_parm_use_partners_roles(self):
        params = self.read_eagle_params()
        return params.get('use_partners_roles', False)

    @api.one
    def _default_tab_profile_part_contracts_list(self):
        profiles = self.get_current_tabs_profile()
        return profiles.get('part_contracts_list', False)

    @api.one
    @api.depends('name')
    def _get_comp_name(self):
        return dict(self.name_get(self._cr, self._uid, self._ids, context=self._context))

    contract_roles_id = fields.One2many('eagle.contract.partner_role', 'partner_id', string='Roles')
    eagle_contracts = fields.Many2many(
        'eagle.contract', 'eagle_contract_partner_rel', 'partner_id', 'contract_id',
        string='Present in files',
        copy=False)
    comp_name = fields.Char(compute='_get_comp_name', string='Name')
    eagle_contract_list = fields.One2many('eagle.contract', compute='_get_eagle_contract_list', string='Files list')
    eagle_contract_count = fields.Integer(compute='_get_eagle_contract_list', string='Files count')

    eagle_parm_use_partners_roles = fields.Boolean(
        compute='_get_eagle_params',
        string='Uses partners roles list?',
        default=lambda self: self._default_parm_use_partners_roles)

    eagle_tab_profile_part_contracts_list = fields.Boolean(
        compute='check_tabs_profile',
        string='eagle_tab_profile_part_contracts_list',
        default=lambda self: self._default_tab_profile_part_contracts_list)

    @api.multi
    def _get_eagle_params(self):
        params = self.env['eagle.contract'].read_eagle_params()

        for part in self:
            part.use_partners_roles = params.get('use_partners_roles', False)


    @api.multi
    def check_tabs_profile(self):
        profiles = self.env['eagle.contract'].get_current_tabs_profile()

        for part in self:
            part.eagle_tab_profile_part_roles = profiles.get('part_roles', False)


    @api.multi
    def _get_eagle_contract_list(self):
        for part in self:
            res = []
            ref_partner = part.parent_id or part
            p_list = [p.id for p in ref_partner.child_ids]
            if p_list:
                items = self.env['eagle.contract'].search(['|', ('partners', 'in', p_list), ('customer_id', 'in', p_list)])
                if items:
                    res = list(OrderedDict.fromkeys(items))

            part.eagle_contract_list = res
            part.eagle_contract_count = len(res)


class eagle_contract(models.Model):
    _inherit = 'eagle.contract'
    
    partner_roles_id = fields.One2many(
        'eagle.contract.partner_role',
        'contract_id',
        string='Partners roles',
        copy=False)

