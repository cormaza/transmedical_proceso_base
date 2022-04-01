from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    beneficiary_ids = fields.One2many("medical.beneficts", "contract_id", string="Beneficiaries")
    copay_percentage = fields.Float(
        string="Copay %",
        required=True,
        default=20,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Reference Invoice",
        domain=[("state", "=", "posted"), ("type", "=", "out_invoice"), ("l10n_latam_internal_type", "=", "invoice")],
    )
    state = fields.Selection(
        selection=[("active", "Active"), ("inactive", "Inactive"), ("cancel", "Cancell")],
        string="Status",
        readonly=True,
        copy=False,
        default="active",
    )
    change_state = fields.Selection(
        selection=[("active", "Active"), ("inactive", "Inactive"), ("cancel", "Cancell")],
        string="Status",
        required=True,
        copy=False,
        default="active",
    )
    tag_ids = fields.Many2many(comodel_name="contract.tag", string="Type Contract")

    @api.onchange("change_state")
    def _onchange_state(self):
        self.state = self.change_state

    @api.constrains("invoice_id")
    def _unique_invoice_id(self):
        for record in self:
            if self.env["contract.contract"].search(
                [("invoice_id", "=", record.invoice_id.id), ("id", "!=", record.id)]
            ):
                raise UserError(_("Invoice already linked to a contract"))

    def name_get(self):
        result = []
        for rec in self:
            name = "{} - {}".format(rec.code, rec.name)
            result.append((rec.id, name))
        return result
