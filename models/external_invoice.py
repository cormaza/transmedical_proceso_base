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
    contract_id = fields.Many2one(comodel_name="contract.contract", readonly=True, string="Contract", required=False)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True, string="Partner", required=False)
    product_id = fields.Many2one(comodel_name="product.product", readonly=True, string="Product", required=False)

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
            rec_data = {
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
                if not current_rec.contract_id:
                    current_rec.sudo().write(rec_data)
            else:
                current_rec = self.sudo().create([rec_data])
            res["id"] = current_rec.id
        return res

    def action_create_contract(self):
        contract_model = self.env["contract.contract"]
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
            if current_country.code == "EC":
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
                "l10n_latam_identification_type_id": type_identification,
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
            default_product = product_model.search(
                [
                    ("default_code", "=", rec.product_code),
                ],
                limit=1,
            )
            if default_product:
                rec.product_id = default_product.id
            if not default_product:
                raise UserError(_("Can't find product with code %s") % (rec.product_code))
            if not rec.contract_id:
                contract_data = contract_model.default_get([])
                contract_data.update(
                    {
                        "partner_id": rec.partner_id.id,
                        "invoice_partner_id": rec.partner_id.id,
                        "contract_line_fixed_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": rec.product_id.id,
                                    "name": ("%s #START# - #END#" % rec.product_id.display_name),
                                    "quantity": rec.product_quantity,
                                    "uom_id": rec.product_id.uom_id.id,
                                    "specific_price": rec.product_price_unit,
                                    "price_unit": rec.product_price_unit,
                                },
                            )
                        ],
                    }
                )
                rec.contract_id = contract_model.create(contract_data).id
                rec.contract_id._recurring_create_invoice(fields.Date.today())
        return True

    @api.model
    def action_cron_generate_invoices(self):
        pending_invoices = self.search([("contract_id", "=", False)])
        if pending_invoices:
            for external_invoice in pending_invoices:
                try:
                    external_invoice.action_create_contract()
                except Exception as e:
                    _logger.debug(_("Error creating contract: %s: %s") % (external_invoice.display_name, str(e)))
