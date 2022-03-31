from odoo import _, models


class ReportInvoiceXLSX(models.AbstractModel):
    _name = "report.l10n_ec_reports.report_invoice_customer_xlsx"
    _inherit = "report.l10n_ec_reports.report_invoice_customer_xlsx"

    def hook_add_new_header(self, header):
        header_new = {
            "r_days_credit": {
                "header": {"value": _("Days of Credits")},
                "data": {"value": self._render("days_credit")},
                "width": 20,
            },
            "o_type_contract": {
                "header": {"value": _("Type Contract")},
                "data": {"value": self._render("type_contract")},
                "width": 20,
            },
            "p_effective_date": {
                "header": {"value": _("Effective date")},
                "data": {"value": self._render("effective_date")},
                "width": 20,
            },
            "q_code_contract": {
                "header": {"value": _("Code Contract")},
                "data": {"value": self._render("code_contract")},
                "width": 20,
            },
            "partner_contract_id": {
                "header": {"value": _("Partner Contract")},
                "data": {"value": self._render("partner_contract_id")},
                "width": 20,
            },
            "payment_method": {
                "header": {"value": _("Payment Method")},
                "data": {"value": self._render("payment_method")},
                "width": 20,
            },
        }
        header.update(header_new)
        return header

    def hook_add_invoice_data(self, invoice_data, invoice):
        invoice_data.update(
            {
                "days_credit": str(invoice.invoice_date_due) or 0,
                "type_contract": ",".join(invoice.mapped("medical_contract_id.tag_ids.name")),
                "effective_date": ",".join(invoice.mapped("medical_contract_id.date_end"))
                if any(invoice.mapped("medical_contract_id.date_end"))
                else "",
                "code_contract": ",".join(invoice.mapped("medical_contract_id.code"))
                if any(invoice.mapped("medical_contract_id.code"))
                else "",
                "partner_contract_id": ",".join(invoice.mapped("medical_contract_id.partner_id.name"))
                if any(invoice.mapped("medical_contract_id.partner_id.name"))
                else "",
                "payment_method": invoice.payment_mode_id.name or "",
            }
        )
        return invoice_data
