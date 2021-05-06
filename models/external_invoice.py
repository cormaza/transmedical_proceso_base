import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountExternalInvoice(models.Model):

    _name = "account.external.invoice"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    partner_name = fields.Char(string="Partner name", readonly=True, required=False)
    partner_vat = fields.Char(string="Partner Vat", readonly=True, required=False)
    partner_street = fields.Char(string="Partner street", readonly=True, required=False)
    partner_phone = fields.Char(string="Partner phone", readonly=True, required=False)
    partner_email = fields.Char(string="Partner email", readonly=True, required=False)
    partner_country = fields.Char(string="Partner country", readonly=True, required=False)
    product_code = fields.Char(string="Product Code", readonly=True, required=False)
    product_quantity = fields.Float(string="Product Code", readonly=True, required=False)
    product_price_unit = fields.Float(string="Product Code", readonly=True, required=False)
    external_reference = fields.Char(string="External reference", readonly=True, required=False)
    payment_amount = fields.Float(string="Payment amount", readonly=True, required=False)
    invoice_id = fields.Many2one(comodel_name="account.move", readonly=True, string="Invoice", required=False)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True, string="Partner", required=False)

    def name_get(self):
        res = []
        for r in self:
            name = "{} ({}) {}".format(r.external_reference, r.payment_amount, r.partner_id.display_name)
            res.append((r.id, name))
        return res

    def create_invoices(self, vals):
        res = {}
        if len(vals) > 1:
            return {
                "error": _("You must send one invoice for call"),
            }
        for data in vals:
            current_rec = self.search(
                [
                    ("external_reference", "=", data.get("external_reference")),
                ]
            )
            invoice_data = {
                "partner_name": data.get("partner_name"),
                "partner_vat": data.get("partner_vat"),
                "partner_street": data.get("partner_street"),
                "partner_phone": data.get("partner_phone"),
                "partner_email": data.get("partner_email"),
                "partner_country": data.get("partner_country"),
                "product_code": data.get("product_code"),
                "product_quantity": data.get("product_quantity"),
                "product_price_unit": data.get("product_price_unit"),
                "external_reference": data.get("external_reference"),
                "payment_amount": data.get("payment_amount"),
            }
            if current_rec:
                if not current_rec.invoice_id:
                    current_rec.sudo().write(invoice_data)
            else:
                current_rec = self.sudo().create([invoice_data])
            res["id"] = current_rec.id
        return res

    def action_create_invoice(self):
        invoice_model = self.env["account.move"].sudo()
        product_model = self.env["product.product"].sudo()
        partner_model = self.env["res.partner"].sudo()
        country_model = self.env["res.country"].sudo()
        it_ruc = self.env.ref("l10n_ec_niif.it_ruc")
        it_cedula = self.env.ref("l10n_ec_niif.it_cedula")
        it_pasaporte = self.env.ref("l10n_ec_niif.it_pasaporte")
        for rec in self:
            current_country = country_model.search(
                [
                    "|",
                    ("name", "ilike", rec.partner_country),
                    ("code", "ilike", rec.partner_country),
                ],
                limit=1,
            )
            type_identification = False
            if current_country.code == 'EC':
                if len(rec.partner_vat) == 10:
                    type_identification = it_cedula.id
                elif len(rec.partner_vat) == 13:
                    type_identification = it_ruc.id
            else:
                type_identification = it_pasaporte.id
            partner_data = {
                "name": rec.partner_name,
                "vat": rec.partner_vat,
                "street": rec.partner_street or current_country.display_name,
                "phone": rec.partner_phone,
                "email": rec.partner_email,
                "country_id": current_country.id,
                'l10n_latam_identification_type_id': type_identification,
            }
            current_partner = partner_model.search(
                [
                    ("vat", "=", rec.partner_vat),
                ]
            )
            if current_partner:
                current_partner.write(partner_data)
            else:
                current_partner = partner_model.create(partner_data)
            if not rec.partner_id:
                rec.partner_id = current_partner.id
            default_product = product_model.search([
                ('default_code', '=', rec.product_code),
            ])
            if not default_product.property_account_income_id:
                raise UserError(_("You must configure income account in product %s") % (default_product.display_name))
            default_printer = self.env.user.get_default_point_of_emission()["default_printer_default_id"]
            if not rec.invoice_id:
                journal = invoice_model.with_context(default_type="out_invoice")._get_default_journal()
                # CHECK ME? me pasa el valor incluido iva siempre?
                price_unit = rec.product_price_unit
                if default_product.taxes_id:
                    price_unit = rec.payment_amount / (1 + (default_product.taxes_id[0].amount / 100.0))
                (
                    next_number,
                    auth_line,
                ) = default_printer.get_next_value_sequence("out_invoice", False, False)
                invoice_data = {
                    "ref": rec.external_reference or "",
                    "type": "out_invoice",
                    "partner_id": rec.partner_id.id,
                    "journal_id": journal.id,
                    "invoice_origin": rec.external_reference,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": default_product.display_name,
                                "product_id": default_product.id,
                                "product_uom_id": default_product.uom_id.id,
                                "quantity": rec.product_quantity,
                                "price_unit": price_unit,
                                "tax_ids": default_product.taxes_id and [(6, 0, default_product.taxes_id.ids)] or [],
                            },
                        )
                    ],
                    "company_id": self.env.company.id,
                    "l10n_ec_point_of_emission_id": default_printer.id,
                    "l10n_latam_document_number": next_number,
                    "l10n_ec_authorization_line_id": auth_line.id,
                    "l10n_ec_type_emission": default_printer.type_emission,
                }
                new_invoice = invoice_model.with_context(default_type="out_invoice").create(invoice_data)
                rec.invoice_id = new_invoice.id
                new_invoice.message_post_with_view(
                    "mail.message_origin_link",
                    values={"self": new_invoice, "origin": rec},
                    subtype_id=self.env.ref("mail.mt_note").id,
                )
                new_invoice.action_post()
        return True

    @api.model
    def action_cron_generate_invoices(self):
        pending_invoices = self.search([("invoice_id", "=", False)])
        if pending_invoices:
            for external_invoice in pending_invoices:
                try:
                    external_invoice.action_create_invoice()
                except Exception as e:
                    _logger.debug(_("Error creating invoice: %s: %s") % (external_invoice.display_name, str(e)))
