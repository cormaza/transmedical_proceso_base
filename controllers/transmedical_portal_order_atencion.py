import json

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager



class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        partner = request.env.user.partner_id
        AtencionOrder = request.env['medical.attention.order']
        return values

    @http.route(['/my/atencion_order', '/my/atencion_order/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AtencionOrder = request.env['medical.attention.order']

        domain = [
            ('state', 'in', ['approved', 'liquidated'])
        ]

        searchbar_sortings = {
            'issue_date': {'label': _('Issue Date'), 'order': 'issue_date'},
            'number': {'label': _('Number'), 'order': 'number'},
        }
        if not sortby:
            sortby = 'number'
        sort_order = searchbar_sortings[sortby]['order']

        quotation_count = AtencionOrder.search_count(domain)

        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        quotations = AtencionOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("transmedical_proceso_base.medical_atention_order_portal_template", values)


