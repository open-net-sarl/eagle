# -*- coding: utf-8 -*-
# Copyright 2017 Open Net Sàrl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Calc short_descr
"""


def migrate(cr, version):
    if not version:
        return

    query = ("UPDATE sale_subscription_line l "
            "SET short_descr='[' || p.default_code || '] ' || t.name from product_template t, product_product p where l.product_id=p.id and p.product_tmpl_id=t.id")
    cr.execute(query)

    query = ("UPDATE sale_order_line l "
            "SET short_descr='[' || p.default_code || '] ' || t.name from product_template t, product_product p where l.product_id=p.id and p.product_tmpl_id=t.id")
    cr.execute(query)
