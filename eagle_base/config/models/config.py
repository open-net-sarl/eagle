# -*- coding: utf-8 -*-
#
#  File: config/config.py
#  Module: eagle_base
#  Eagle's config management
#
#  Created by cyp@open-net.ch
#
#   Starting with the version 5.0, Eagle's parameters are not any more managed
#   using the old, classic way, but rather through OE V7 configuration management:
#   Each time the settings are saved, Eagle's parameters are stored.
#
#  Copyright (c) 2011-TODAY Open-Net Ltd. <http://www.open-net.ch>

from openerp import models, fields, api, _
from openerp.models import MAGIC_COLUMNS

import logging
_logger = logging.getLogger(__name__)

class EagleConfigParams(models.Model):
    _name = 'eagle.config.params'
    _description = 'Eagle Configuration Parameters'
    
    # ---------- Fields management

    name = fields.Char(
        string='Name',
        default='Eagle Parameters'
    )
    use_members_list = fields.Boolean(
        string='Uses members list',
        default=False
    )
    use_partners_list = fields.Boolean(
        string='Uses partners list',
        default=False
    )
    use_partners_roles = fields.Boolean(
        string='Uses partners roles',
        default=False
    )
    auto_production_state = fields.Boolean(
        string="Automatic 'Production state' mode?",
        default=True
    )
    close_to_draft = fields.Boolean(
        string="Can re-open a contract?"
    )
    use_cn_seq = fields.Boolean(
        string="Use the contract sequences",
        default=False
    )
    date_format = fields.Char(
        string='Customized date format',
        default='%d.%m.%Y'
    )

    tabs = fields.Char(string='Tabs list')
    tabs_profile = fields.Many2one('eagle.config.tabs_profile', string='Tabs profile')

    void = fields.Char(' ', size=1, default=' ')

    # ---------- Instances management

    def copy(self, cr, uid, id, default={}, context={}):
        raise osv.except_osv(_('Forbidden!'), _('Eagle must have one and only one record.'))
    
    @api.model
    def get_instance(self, as_dict=False):
        params = self.search([], limit=1)
        if not params or not as_dict:
            return params

        return params.read()[0]


class EagleConfigSettings(models.TransientModel):
    _name = 'eagle.config.settings'
    _inherit = 'res.config.settings'

    # ---------- Fields management

    name = fields.Char(string='Name', default='Eagle Parameters')
    use_members_list = fields.Boolean(
        string='Uses members list',
        default=False
    )
    use_partners_list = fields.Boolean(
        string='Uses partners list',
        default=False
    )
    use_partners_roles = fields.Boolean(
        string='Uses partners roles',
        default=False
    )
    auto_production_state = fields.Boolean(string="Automatic 'Production state' mode?", default=True)
    close_to_draft = fields.Boolean(string="Can re-open a contract?")
    use_cn_seq = fields.Boolean(string="Use the contract sequences", default=False)
    date_format = fields.Char(string='Date format', size=15, default='%d.%m.%Y')

    tabs = fields.Char(string='Tabs list')
    tabs_profile = fields.Many2one('eagle.config.tabs_profile', string='Tabs profile')

    # ---------- Instances management
    
    def copy_vals(self, rec):
        ret = {}
        if not rec:
            return ret
        for fname, field in self._fields.iteritems():
            if fname in MAGIC_COLUMNS:
                continue
            if field.compute or field.company_dependent or field.type in ['serialized','dummy','sparse']:
                continue
            if field.relational:
                if field.type == 'many2one' and rec.get(fname, False):
                    ret[fname] = rec[fname][0]
                continue
            if fname in rec:
                ret[fname] = rec[fname]
        
        return ret

    @api.model
    def default_get(self, fields_list):
        params = self.env['eagle.config.params'].get_instance(as_dict=True)
        
        ret = self.copy_vals(params)
        if ret.get('date_format', False):
            ret['date_format'] = '%d.%m.%Y'
        return ret
        
    def _setup_menu_action(self, cr, uid, xml_id, flag, context={}):
        model_obj = self.pool.get("ir.model.data")
        obj = model_obj.xmlid_to_object(cr, uid, xml_id, raise_if_not_found=False, context=context)
        if not obj:
            return False
        if not flag:
            lst = [
                'eagle_base.group_contracts_viewers',
                'eagle_base.group_contracts_editors',
                'eagle_base.group_contracts_managers',
                'eagle_base.group_contracts_users'
            ]
        else:
            lst = ['base.group_no_one']
        lst_ids = []
        for item in lst:
            t = model_obj.xmlid_to_res_model_res_id(cr, uid, item, False)
            res_model, res_id = t
            if res_id:
                lst_ids.append(res_id)
        obj.write({'groups_id':[(6,0,lst_ids)]})
        
        return True

    def execute(self, cr, uid, ids, context=None):
        eagle_cfg_param_obj = self.pool.get('eagle.config.params')

        rec = self.read(cr, uid, ids[0], [], context)
        vals = self.copy_vals(rec)

        # Create/update Eagle's parameters
        rec_ids = eagle_cfg_param_obj.search(cr, uid, [], context=context)
        if not rec_ids:
            vals['name'] = 'Eagle Parameters'
            rec_id = eagle_cfg_param_obj.create(cr, uid, vals, context=context)
        else:
            rec_id = rec_ids[0]
            eagle_cfg_param_obj.write(cr, uid, [rec_id], vals, context=context)
        
        # Show/Hide some of the menu items, depending on the automatic mode settings
        self._setup_menu_action(cr, uid, 
                'eagle_base.eagle_menu_contracts_inst_form', 
                self.pool.get('eagle.contract').get_eagle_param(cr, uid, 'auto_production_state', False),
                context=context)

        # force client-side reload (update user menu and current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
 
