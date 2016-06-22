# -*- coding: utf-8 -*-
#
#  File: config/wizard/wiz_tabs_profile.py
#  Module: eagle_base
#
#  Created by cyp@open-net.ch
#
#   Starting the version 5.0, this tabs profile wizard is using
#   OE's standard mecanism to implement a completely dynamic fields list management
#   This has been introduced since the old wizard.interface class has been deprecated. 
#
#  Copyright (c) 2014-TODAY Open-Net Ltd. <http://www.open-net.ch>

from lxml import etree

from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class EagleWizTabsProfile(models.TransientModel):
    _name = 'eagle.wiz_tabs_profile'
    _description = 'Eagle wizard: setup a tabs profile'
    _profile_name = ''

    # ------------------------- Fields management

    @api.model
    def _default_profile(self):
        record = None
        if self._context.get('active_id', False) and self._context.get('active_model', False):
            record = self.env[self._context['active_model']].browse(self._context['active_id'])

        return record and record.name or ''

    name = fields.Char(string='Profile', default=_default_profile)

    # ---------- Interface management

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context: context = {}

        # Let the system fully load the view
        res = super(EagleWizTabsProfile, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if view_type != 'form':
            return res

        # Dynamically define the needed fields
        tab_profiles_obj = self.pool.get('eagle.config.tabs_profile')
        modules = {}
        flds = {}
        for fld, label in tab_profiles_obj.tabs_list.items():
            t = label.split(': ')
            if t[0] not in modules:
                modules[t[0]] = []
            modules[t[0]].append(fld)
            flds[fld] = {
                'selectable': True,
                'string': _(t[1]),
                'type': 'boolean',
                'views': {}
            }
        if flds:
            res['fields'].update(flds)

        # Update the FORM definition with the complementary fields
        eview = etree.fromstring(res['arch'])
        if context.get('active_model') and context.get('active_id'):
            this_name = self.pool.get(context['active_model']).read(cr, uid, context['active_id'], ['name'])['name']
            for label in eview.xpath("//label[@string=' ']"):
                label.set('string', _('Profile: ') + this_name)
        for placeholder in eview.xpath("//page[@name='placeholder']"):
            for module_name in sorted(modules):

                div = etree.Element('group', {'colspan':'4', 'col':'8'})
                for i in range(len(modules[module_name])):
                    div.append(etree.Element('field', {'name': modules[module_name][i]}))

                page = etree.Element('page', {'string': module_name})
                page.append(div)

                placeholder.addprevious(page)

            placeholder.getparent().remove(placeholder)
        res['arch'] = etree.tostring(eview)

        return res

    @api.model
    def default_get(self, fields_list):
        ret = super(EagleWizTabsProfile, self).default_get(fields_list)

        # Retrieve the current tabs selection and update the default values
        active_tabs = []
        if self._context.get('active_id') and self._context.get('active_model','') == 'eagle.config.tabs_profile':
            rec = self.env[self._context['active_model']].browse(self._context['active_id'])
            if rec:
                active_tabs = rec.opts.split(';') if rec.opts else []
        for active_tab in active_tabs:
            ret.update({active_tab:True})

        return ret

    @api.model
    def create(self, values):

        # Retrieve the needed fields
        tab_profiles_obj = self.env['eagle.config.tabs_profile']

        # Retrieve and store the selected tabs
        vals = [fld for fld in values if fld in tab_profiles_obj.tabs_list and values[fld]]
        if self._context.get('active_id') and self._context.get('active_model','') == 'eagle.config.tabs_profile':
            self.env[self._context['active_model']].browse(self._context['active_id']).write({'opts': ';'.join(vals)})

        #Before returning to caller, let's remove the suppl. fields
        for fld, label in tab_profiles_obj.tabs_list.items():
            if fld in self._columns:
                del self._columns[fld]

        # Return to caller
        return super(EagleWizTabsProfile, self).create({'name':values.get('name','?')})

    @api.one
    def do_save(self):
        return {}

