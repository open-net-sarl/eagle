# -*- coding: utf-8 -*-
#
#  File: contracts.py
#  Module: eagle_crm
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2014 Open-Net Ltd. All rights reserved.
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

from osv import fields, osv
from tools.translate import _
import pytz

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser

from email.Utils import make_msgid
from openerp.addons.base.ir import ir_mail_server
import openerp.tools as tools
import cgi
import html2text

import logging
_logger = logging.getLogger(__name__)

class eagle_contract( osv.osv ):
    _inherit = 'eagle.contract'

    # ---------- Eagle management
    
    def check_tabs_profile(self, cr, uid, cnt_ids, field_names, args, context={}):
        return super(eagle_contract, self).check_tabs_profile(cr, uid, cnt_ids, field_names, args, context=context)
    
    # ---------- Fields management

    def _get_partners_lists(self, cr, uid, cnt_ids, field_name, args, context={}):
        ret = {}
        for cnt in self.browse(cr, uid, cnt_ids, context=context):
            lst_crm = ["<li> - %s</li>" % x.partner_id.comp_name for x in cnt.eagle_crm_ids]
            ret[cnt.id] = '\n'.join(lst_crm)
        
        return ret
    
    def _get_auto_reminder_flag(self, cr, uid, cnt_ids, field_name, args, context={}):
        state = False
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params and eagle_params.auto_reminder_flag:
            state = True
        
        ret = dict.fromkeys(cnt_ids, False)
        for filtered_id in self.search(cr, uid, [('id','in',cnt_ids),('state', 'in', ['draft','confirm'])], context=context):
            ret[filtered_id] = state        
        
        return ret
    
    def _comp_current_reminder(self, cr, uid, cnt_ids, field_name, args, context={}):
        state = False
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params and eagle_params.auto_reminder_flag:
            state = True

        ret = {}
        for cnt in self.read(cr, uid, cnt_ids, ['auto_reminder_date','auto_reminder_flag','reminder_timestamp','reminder_flag'], context=context):
            dt1 = False
            if state:
                dt1 = cnt.get('auto_reminder_date', False)
            
            dt2 = cnt.get('reminder_timestamp', False)
            if not cnt.get('reminder_flag', False):
                dt2 = False

            if not dt1 or (dt2 and (dt1 > dt2)):
                dt1 = dt2
            
            ret[cnt['id']] = dt1
        
        return ret
    
    def _detect_reminders_from_ids(self, cr, uid, ids, context={}):
        ret_ids = self.search(cr, uid, [('id','in',ids),('reminder_flag','!=',False)], context=context)
        
        return ret_ids

    _columns = {
        'eagle_crm_ids': fields.one2many('eagle.crm', 'contract_id', 'CRM'),
        'crm_partners': fields.function(_get_partners_lists, method=True, type='char', readonly=True, string='CRM Partners', store=False),
        'probability': fields.float('Success Rate (%)',group_operator="avg"),
        'planned_revenue': fields.float('Expected Revenue', track_visibility='always'),
        'crm_currency_id': fields.many2one('res.currency', 'Currency'),
        'crm_stage_id': fields.many2one('crm.case.stage', 'CRM stage', track_visibility='onchange'),

        'src_crm_if_lead': fields.many2one('crm.lead', 'Source'),
        'src_crm_if_opport': fields.many2one('crm.lead', 'Source'),
        
        'auto_reminder_date': fields.datetime('Automatic reminder'),
        'auto_reminder_flag': fields.function(_get_auto_reminder_flag, method=True, type='boolean', string='Use reminder', readonly=True, store=False),
        'reminder_timestamp': fields.datetime('Next reminder'),
        'reminder_flag': fields.boolean('Use reminder'),
        'current_reminder': fields.function( _comp_current_reminder, type='datetime', method=True, string='Reminder', store={
                'eagle.contract': (_detect_reminders_from_ids, ['reminder_timestamp','reminder_flag'], 10)
                }
            ),

        'view_color': fields.integer('Color Index'),
        'tab_profile_eagle_crm': fields.function( check_tabs_profile, method=True, type='boolean', string='tab_profile_eagle_crm', multi='tab_profile_eagle_crm' ),
    }

    _sql_constraints = [
        ('check_probability', 'check(probability >= 0 and probability <= 100)', 'The probability of closing the deal should be between 0% and 100%!')
    ]

    # ---------- Interface related

    def do_open_crm_list(self, cr, uid, ids, context={}):
    
        for cnt in self.read(cr, uid, ids, ['name','eagle_crm_ids'], context=context):
            
            res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'eagle_crm', 'eagle_action_eagle_crm_cnt', context)
            res['context'] = {'default_contract_id':cnt['id']}
            res['domain'] = [('id','in',cnt.get('eagle_crm_ids', [-1]))]
            
            return res

        return {}

    # ---------- Instance management
    
    def write(self, cr, uid, ids, vals, context={}):
        # Detect if there's a pending change of state
        new_state = False
        context = context or {}
        stage_obj = self.pool.get('crm.case.stage')
        if vals.get('crm_stage_id', False):
            stage = stage_obj.browse(cr, uid, vals['crm_stage_id'], context=context)
            if stage and stage.eagle_state:
                new_state = stage.eagle_state
        elif vals.get('state', False) and not context.get('ignore_state', False):
            stage_ids = stage_obj.search(cr, uid, [('eagle_state','=',vals['state'])], context=context)
            if stage_ids:
                vals['crm_stage_id'] = stage_ids[0]
                
        # Standard processing
        ret = super(eagle_contract, self).write(cr, uid, ids, vals, context=context)

        # Manage the reminders
        eagle_params = self.pool.get('eagle.config.params').get_instance(cr, uid, context=context)
        if eagle_params and eagle_params.auto_reminder_flag and eagle_params.auto_reminder_delay:
            # 1st update: the auto reminder
            query = 'Update eagle_contract set auto_reminder_date=(write_date::date + interval \'%s days\')::date where id in %s and state in %s'
            cr.execute(query, (eagle_params.auto_reminder_delay, tuple(ids),('draft','confirm')))
            # then: current = first date between the automatic and the manual reminder, for those with a manual reminder
            query = 'Update eagle_contract set current_reminder= case when auto_reminder_date::timestamp > reminder_timestamp then reminder_timestamp else auto_reminder_date::timestamp end where reminder_flag is true and id in %s and state in %s'
            cr.execute(query, (tuple(ids), ('draft','confirm')))
            # in the end: current = automatic for those with no manual reminder
            query = 'Update eagle_contract set current_reminder=auto_reminder_date where reminder_flag is not true and id in %s and state in %s'
            cr.execute(query, (tuple(ids), ('draft','confirm')))
            # by the way, the current reminder is also recomputed each time the manual reminder is changed.
        
        # Manage the change of state, if any
        if new_state:
            if isinstance(ids,(int,long)): ids = [ids]
            ctx = context.copy()
            ctx['ignore_state'] = True
            for row in self.read(cr, uid, ids, ['state'], context=ctx):
                if row.get('state', '') != new_state:
                    event_cfg_name = self.pool.get('eagle.config.event').get_name_by_state(cr, uid, False, new_state)
                    self.handle_event(cr, uid, [row['id']], event_cfg_name, context=ctx)
        
        return ret
    
    # ---------- Scheduler management
    
    def run_manual_reminders(self, cr, uid, nb_days, context={}):
        context = context or {}
        date_from = datetime.now().strftime('%Y-%m-%d 00:00:00')
        date_to = (parser.parse(date_from) + relativedelta(days=nb_days-1)).strftime('%Y-%m-%d 23:59:59')
        
        filter = [
            ('current_reminder', '>=', date_from),
            ('current_reminder', '<=', date_to),
            ('reminder_flag', '!=', False),
            ('reminder_timestamp', '!=', False),
             ('state', 'in', ['draft','confirm']),
        ]
        ids = self.search(cr, uid, filter, context=context)

        _logger.info("Starting the Eagle CRM manual reminder: from " + str(date_from) + " to " + str(date_to) + ", %d elements to check" % len(ids))
        
        to_sent = {}
        for cnt in self.browse(cr, uid, ids, context=context):
            if not cnt.user_id.user_email:
                continue
            if cnt.user_id.email not in to_sent:
                to_sent[cnt.user_id.email] = []
            to_sent[cnt.user_id.email].append(cnt)
        
        mail_server = self.pool.get('ir.mail_server')

        for email, cnt_list in to_sent.items():
            lst = []
            for cnt in cnt_list:
                # Compute the line of text, handle correctly the time zone
                utc = pytz.timezone('UTC')
                context_tz = pytz.timezone(cnt.user_id.tz)
                utc_timestamp = utc.localize(parser.parse(cnt.current_reminder), is_dst=False) # UTC = no DST
                txt = utc_timestamp.astimezone(context_tz).strftime("%A %d.%m %H:%M") + ": %s" % cnt.name

                # Transform this into a decent html line
                h = html2text.HTML2Text()
                h.ignore_links = True
                tmp = cgi.escape(h.handle(txt))
                lst.append(tmp)

            if not lst:
                continue
            body_html = '<br/>\n'.join(lst)
            
            message_id = make_msgid()
            msg = mail_server.build_email(
                False,
                ['cyp@open-net.ch'],
                u"Rappels du " + parser.parse(date_from).strftime("%d.%m") + u" au " + parser.parse(date_to).strftime("%d.%m") + " pour " + email,
                body_html,
                body_alternative = tools.plaintext2html(body_html),
                email_cc = False,
                attachments = False,
                message_id = ir_mail_server.encode_header(message_id),
                references = False,
                object_id = False,
                subtype = 'html',
                subtype_alternative = 'plain')
            
            mail_server.send_email(cr, uid, msg)
        
        _logger.info("End of the Eagle CRM manual reminder")
        return True

eagle_contract()

