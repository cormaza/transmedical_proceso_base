import base64
import json
from collections import OrderedDict

from odoo import http, _
from odoo.http import request, content_disposition
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager



class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        partner = request.env.user.partner_id.id
        domain = []
        AtentionOrder = request.env['medical.attention.order']
        values['medical_atention_order_count'] = AtentionOrder.search_count(domain)
        return values

    @http.route(['/my/atention_order', '/my/atention_order/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_medical_atention_order(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AtentionOrder = request.env['medical.attention.order']

        domain = []

        searchbar_sortings = {
            'issue_date': {'label': _('Issue Date'), 'order': 'issue_date'},
            'number': {'label': _('Number'), 'order': 'number'},
        }
        if not sortby:
            sortby = 'number'
        sort_order = searchbar_sortings[sortby]['order']

        medical_atention_order_count = AtentionOrder.search_count(domain)
        filterby = "all"
        pager = portal_pager(
            url="/my/atention_order",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "filterby": filterby,
            },
            total=medical_atention_order_count,
            page=page,
            step=self._items_per_page,
        )
        atention_order = AtentionOrder.search(
            domain, order=sort_order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session['my_atention_order_history'] = atention_order.ids[:100]
        values.update({
            'date': date_begin,
            'page_name': 'atention_order',
            'pager': pager,
            'medical_atention_order_count': medical_atention_order_count,
            "atention_order": atention_order,
            'default_url': '/my/atention_order',
            "searchbar_sortings": OrderedDict(sorted(searchbar_sortings.items())),
            "sortby": sortby,
            "filterby": filterby,
        })
        return request.render("transmedical_proceso_base.portal_my_atention_order", values)

    def _atention_order_get_page_view_values(self, atention_order, access_token, **kwargs):
        values = {
            "page_name": "atention_order",
            "atention_order": atention_order,
        }
        return self._get_page_view_values(
            atention_order,
            access_token,
            values,
            "my_atention_order_history",
            False,
            **kwargs,
        )

    @http.route(
        ["/my/atention_order/<int:medical_order_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_medical_order_detail(
        self,
        medical_order_id,
        access_token=None,
        report_type=None,
        download=False,
        **kw,
    ):
        atention_order_sudo = self._document_check_access("medical.attention.order", medical_order_id, access_token)
        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=atention_order_sudo,
                report_type=report_type,
                report_ref="transmedical_proceso_base.action_template_medical_attention_order",
                download=download,
            )
        values = self._atention_order_get_page_view_values(atention_order_sudo, access_token, **kw)
        return request.render("transmedical_proceso_base.portal_atention_order_page", values)

