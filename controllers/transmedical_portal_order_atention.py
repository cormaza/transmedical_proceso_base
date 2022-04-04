from collections import OrderedDict

from odoo import _, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        domain = []
        AtentionOrder = request.env["medical.attention.order"]
        MedicalLiquidation = request.env["medical.liquidation"]
        values["medical_atention_order_count"] = AtentionOrder.search_count(domain)
        values["medical_liquidation_count"] = MedicalLiquidation.search_count(domain)
        return values

    @http.route(["/my/atention_order", "/my/atention_order/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_medical_atention_order(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        AtentionOrder = request.env["medical.attention.order"]

        domain = []

        searchbar_sortings = {
            "issue_date": {"label": _("Issue Date"), "order": "issue_date"},
            "number": {"label": _("Number"), "order": "number"},
        }
        if not sortby:
            sortby = "number"
        sort_order = searchbar_sortings[sortby]["order"]

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
        request.session["my_atention_order_history"] = atention_order.ids[:100]
        values.update(
            {
                "date": date_begin,
                "page_name": "atention_order",
                "pager": pager,
                "medical_atention_order_count": medical_atention_order_count,
                "atention_order": atention_order,
                "default_url": "/my/atention_order",
                "searchbar_sortings": OrderedDict(sorted(searchbar_sortings.items())),
                "sortby": sortby,
                "filterby": filterby,
            }
        )
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

    @http.route(
        ["/my/medical_liquidation", "/my/medical_liquidation/page/<int:page>"], type="http", auth="user", website=True
    )
    def portal_my_medical_liquidation(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        MedicalLiquidation = request.env["medical.liquidation"]

        domain = []

        searchbar_sortings = {
            "issue_date": {"label": _("Issue Date"), "order": "issue_date"},
            "number": {"label": _("Number"), "order": "number"},
        }
        if not sortby:
            sortby = "number"
        sort_order = searchbar_sortings[sortby]["order"]

        medical_liquidation_count = MedicalLiquidation.search_count(domain)
        filterby = "all"
        pager = portal_pager(
            url="/my/medical_liquidation",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "filterby": filterby,
            },
            total=medical_liquidation_count,
            page=page,
            step=self._items_per_page,
        )
        liquidation_order = MedicalLiquidation.search(
            domain, order=sort_order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_medical_liquidation_history"] = liquidation_order.ids[:100]
        values.update(
            {
                "date": date_begin,
                "page_name": "medical_liquidation",
                "pager": pager,
                "medical_liquidation_count": medical_liquidation_count,
                "medical_liquidation": liquidation_order,
                "default_url": "/my/medical_liquidation",
                "searchbar_sortings": OrderedDict(sorted(searchbar_sortings.items())),
                "sortby": sortby,
                "filterby": filterby,
            }
        )
        return request.render("transmedical_proceso_base.portal_my_medical_liquidation", values)

    def _medical_liquidation_get_page_view_values(self, medical_liquidation, access_token, **kwargs):
        values = {
            "page_name": "medical_liquidation",
            "medical_liquidation": medical_liquidation,
        }
        return self._get_page_view_values(
            medical_liquidation,
            access_token,
            values,
            "my_medical_liquidation_history",
            False,
            **kwargs,
        )

    @http.route(
        ["/my/medical_liquidation/<int:medical_liquidation_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_medical_medical_liquidation_detail(
        self,
        medical_liquidation_id,
        access_token=None,
        report_type=None,
        download=False,
        **kw,
    ):
        liquidation_sudo = self._document_check_access("medical.liquidation", medical_liquidation_id, access_token)
        if report_type in ("html", "pdf", "text"):
            return self._show_report(
                model=liquidation_sudo,
                report_type=report_type,
                report_ref="transmedical_proceso_base.action_template_medical_liquidation",
                download=download,
            )
        values = self._medical_liquidation_get_page_view_values(liquidation_sudo, access_token, **kw)
        return request.render("transmedical_proceso_base.portal_medical_liquidation_page", values)
