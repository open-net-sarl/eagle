# -*- coding: utf-8 -*-
#
#  File: models/leads.py
#  Module: eagle_project
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2016-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp import models, fields, api
from openerp.exceptions import except_orm

import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _default_eagle_files_count(self):
        return len(self.eagle_files_ids)

    @api.model
    def _default_eagle_files_lst(self):
        return [f.name for f in self.eagle_files_ids]

    @api.model
    def _default_default_file_partner(self):
        return self.partner_id.parent_id if self.partner_id.parent_id else self.partner_id

    eagle_files_ids = fields.One2many('eagle.contract', 'opportunity', string='Files')
    eagle_files_lst = fields.Char(compute='_list_eagle_files', string='Files Names', default=_default_eagle_files_lst)
    eagle_files_count = fields.Integer(compute='_list_eagle_files', string='Files nb', default=_default_eagle_files_count)
    default_file_partner = fields.Many2one('res.partner', string='Default file partner',
        compute='_get_default_file_partner', default=_default_default_file_partner)

    @api.multi
    def _list_eagle_files(self):
        for lead in self:
            lead.eagle_files_count = len(lead.eagle_files_ids)
            if lead.eagle_files_count == 0:
                lead.eagle_files_lst = ''
            elif lead.eagle_files_count == 1:
                lead.eagle_files_lst = lead.eagle_files_ids[0].name
            else:
                lead.eagle_files_lst = '\n'.join(["<li> - %s</li>" % f.name for f in lead.eagle_files_ids])

    @api.multi
    def _get_default_file_partner(self):
        for lead in self:
            lead.default_file_partner = lead.partner_id.parent_id if lead.partner_id.parent_id else lead.partner_id

    @api.v7
    def redirect_eagle_file_view(self, cr, uid, ids, context=None):
        lead = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'eagle_base', 'eagle_action_contract_filter_all_tree', context)
        res['domain'] = [('id','in',[x.id for x in lead.eagle_files_ids])]

        return res

