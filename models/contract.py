from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ContractContract(models.Model):
    _inherit = "contract.contract"

    beneficiary_ids = fields.One2many("medical.beneficts", "contract_id", string="Beneficiaries")
    limit_query = fields.Float(string="Limit Query", required=True, track_visibility="onchange")
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
        track_visibility="onchange",
    )
    tag_ids = fields.Many2many(comodel_name="contract.tag", string="Type Contract")
    deductible_ambulatory = fields.Float(
        string="Deductible Ambulatory", required=True, default=20, track_visibility="onchange"
    )
    deductible_hospitalary = fields.Float(
        string="Deductible hospitalary", required=True, default=20, track_visibility="onchange"
    )
    maternity = fields.Float(string="Maternity", required=True, default=20, track_visibility="onchange")
    copage_limit_ids = fields.Many2many("medical.copago.limit", string="Copago_ids")
    date_end = fields.Date(track_visibility="onchange")

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

    def _terminate_contract(self, terminate_reason_id, terminate_comment, terminate_date):
        super(ContractContract, self)._terminate_contract(terminate_reason_id, terminate_comment, terminate_date)
        date_start = fields.Date.today()
        self.with_context(skip_modification_mail=True).write(
            {"modification_ids": [(0, 0, {"date": date_start, "description": _("Contract End")})]}
        )

    def notificacion_expiracion(self):
        for record in self.env["contract.contract"].search([("state", "=", "active")]):
            now = fields.Date.today()
            diff = (now - record.date_start).days
            if diff < 30:
                msg = _("Documento esta por expirar, por favor revisarlo")
                record.message_post(body=msg)

    def renovacion(self):
        for record in self:
            date_start = fields.Date.today()
            self.with_context(skip_modification_mail=False).write(
                {"modification_ids": [(0, 0, {"date": date_start, "description": _("Change Date in Contract")})]}
            )
            record.date_start += relativedelta(years=1)

    @api.onchange("date_end")
    def onchange_end_date(self):
        date_start = fields.Date.today()
        self.with_context(skip_modification_mail=False).write(
            {"modification_ids": [(0, 0, {"date": date_start, "description": _("Change Date in Contract")})]}
        )


class CopagoLimit(models.Model):
    _name = "medical.copago.limit"
    _description = "Model Percentage for procedure"
    _rec_name = "procedure_id"

    procedure_id = fields.Many2one("medical.procedure.type", string="Procedure Type", required=True)
    percentage = fields.Float("Percentage %", digits="Product Price", required=True)
    type_limit = fields.Selection(
        [("inability", "Inability"), ("anual", "Anual")], string="Type Limit", required=True, default="inability"
    )
