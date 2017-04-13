# -*- coding: utf-8 -*-
# © 2017 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby
from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class EagleContract(models.Model):
    _inherit = 'eagle.contract'

    do_page_break = fields.Boolean(
        string="Do a page break between subscriptions types",
        help="Do a page break between recurring and non recurring subscriptions in the report")

    @api.multi
    def subs_lines_layouted(self, filtred_lines):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(filtred_lines, lambda l: l.sale_layout_cat_id):
            # If last added category induced a pagebreak, this one will be on a new page
            if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
                report_pages.append([])
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or 'Uncategorized',
                'subtotal': category and category.subtotal,
                'pagebreak': category and category.pagebreak,
                'lines': list(lines)
            })
        
        new_layout = [[]]

        for page in report_pages:
            for category in page:
                has_page_break = False
                for line in category['lines']:
                    if line.page_break:
                        has_page_break = True
                if has_page_break:
                    _logger.info(category["name"])
                    new_layout[-1].append(category)
                    new_layout.append([])
                else:
                    _logger.info(category["name"])
                    new_layout[-1].append(category)

        return new_layout