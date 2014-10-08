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
#  Copyright (c) 2013 Open-Net Ltd. All rights reserved.
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from lxml import etree
import netsvc

import logging
_logger = logging.getLogger(__name__)

class wiz_tabs_profile(osv.osv_memory):
    _name = 'eagle.wiz_tabs_profile'
    _description = 'Eagle wizard: setup a tabs profile'
    _profile_name = ''

    # ------------------------- Fields related
    
    _columns = {
        'name': fields.char('Profile', size=40),
    }
    
    _defaults = {
        'name': lambda s,c,u,ct: ct.get('active_id') and ct.get('active_model') and s.pool.get(ct['active_model']).read(c,u,ct['active_id'],['name'],context=ct)['name'] or '?'
    }
    
    # ---------- Instances management
    
    def __init__(self, pool, cr):
        super(wiz_tabs_profile, self).__init__(pool, cr)
        
        tab_profiles_obj = pool.get('eagle.config.tabs_profile')
        new_flds = {}
        for fld, label in tab_profiles_obj.tabs_list.items():
            t = label.split(': ')
            new_flds[fld] = fields.boolean(t[1], module=t[0])
        
        self._columns.update(new_flds)
            

    # ---------- Interface related

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if not context: context = {}
        
        # Let the system fully load the view
        res = super(wiz_tabs_profile, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if view_type != 'form': return res

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
            label = eview.xpath("//label[@string=' ']")
            if label:
                label[0].set('string', _('Profile: ') + this_name)
        placeholder = eview.xpath("//page[@name='placeholder']")
        if placeholder:
            placeholder = placeholder[0]
            for module_name in sorted(modules):
                page = etree.Element('page', {'string': module_name})

                div = etree.Element('group', {'colspan':'4', 'col':'8'})

                for i in range(len(modules[module_name])):
                    div.append(etree.Element('field', {'name': modules[module_name][i]}))
                
                page.append(div)
                placeholder.addprevious(page)

            placeholder.getparent().remove(placeholder)
        res['arch'] = etree.tostring(eview)

        return res
    
    def default_get(self, cr, uid, fields_list, context=None):
        ret = super(wiz_tabs_profile, self).default_get(cr, uid, fields_list, context=context)

        # Retrieve the current tabs selection and update the default values
        active_tabs = []
        if context.get('active_id') and context.get('active_model','') == 'eagle.config.tabs_profile':
            rec = self.pool.get(context['active_model']).browse(cr, uid, context['active_id'], context=context)
            if rec:
                active_tabs = rec.opts.split(';') if rec.opts else []
        for active_tab in active_tabs:
            ret.update({active_tab:True})
        
        return ret

    def create(self, cr, uid, values, context=None):

        # Retrieve the needed fields
        tab_profiles_obj = self.pool.get('eagle.config.tabs_profile')

        # Retrieve and store the selected tabs
        vals = [fld for fld in values if fld in tab_profiles_obj.tabs_list and values[fld]]
        if context.get('active_id') and context.get('active_model','') == 'eagle.config.tabs_profile':
            self.pool.get(context['active_model']).write(cr, uid, [context['active_id']], {'opts': ';'.join(vals)}, context=context)
        
        # Return to caller
        return super(wiz_tabs_profile, self).create(cr, uid, {}, context=context)
    
    def do_save(self, cr, uid, ids, context={}):
        return {}
        
wiz_tabs_profile()    
