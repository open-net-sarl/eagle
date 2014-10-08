# -*- encoding: utf-8 -*-
#
#  File: wizard/wiz_cust_delivery_date.py
#  Module: eagle_management
#
#  Created by cyp@open-net.ch
#
#  Copyright (c) 2011 Open-Net Ltd. All rights reserved.
##############################################################################
#
# Author Yvon Philiippe Crittin / Open Net Sarl
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields
import time

class wizard_cust_delivery_date(osv.osv_memory):
	_name = 'eagle.wiz_cust_delivery_date'
	_description = 'Force the Customer Delivery Date on all position to install'
	
	_columns = {
		'cd_date': fields.date( 'New customer delivery date' ),
	}
	_defaults = {
		'cd_date': lambda *a: time.strftime('%Y-%m-%d'),
	}

	def force_date(self, cr, uid, ids, context=None):
		if not context:
			context = {}
		cnt_ids = context.get('active_ids')
		positions = self.pool.get('eagle.contract.position')
		if cnt_ids:
			for data in self.browse(cr, uid, ids):
				cnt_line_ids = positions.search( cr, uid, [('contract_id','in',cnt_ids),('state','=','open')], context=context )
				if cnt_line_ids and len(cnt_line_ids):
					positions.write( cr, uid, cnt_line_ids, {'cust_delivery_date': data.cd_date}, context=context )
		
		return {}

wizard_cust_delivery_date()
