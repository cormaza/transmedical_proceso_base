from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MedicalLiquidation(models.Model):
    _name = "medical.liquidation"
    _description = "medical.liquidation"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "portal.mixin",
    ]
    _rec_name = "number"

    number = fields.Char(string="Number", required=False, readonly=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False)
    issue_date = fields.Datetime(string="Issue date", required=False, default=fields.Date.today())
    reception_date = fields.Date(
        string="Reception date",
        required=False,
        default=fields.Date.today(),
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True)
    contract_id = fields.Many2one(comodel_name="contract.contract", string="Contract", required=False)
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=False,
        domain=[("medical_service_provider", "=", True)],
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("approved", "Approved"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    beneficiary_type = fields.Selection(
        string="Beneficiary type",
        selection=[
            ("personal", "Customer"),
            ("supplier", "Supplier"),
        ],
        required=True,
    )
    liquidation_type = fields.Selection(
        string="Liquidation type",
        selection=[
            ("ambulatory", "Ambulatory"),
            ("hospitable", "Hospitable"),
        ],
        required=True,
    )
    kind_of_care = fields.Selection(
        string="Kind of care",
        selection=[
            ("normal", "Normal"),
            ("pregnancy", "Pregnancy"),
            ("emergency", "Emergency"),
        ],
        required=True,
    )
    concept = fields.Text(string="Concept", required=False)
    invoice_liquidation_ids = fields.One2many(
        comodel_name="medical.liquidation.invoice",
        inverse_name="liquidation_id",
        string="Invoices liquidation",
        required=False,
    )
    max_payment_date = fields.Date(string="Max payment date", required=False)
    total_liquidation = fields.Float(string="Total liquidation", compute="_compute_amounts", required=False)
    attention_order_ids = fields.One2many(
        comodel_name="medical.attention.order", inverse_name="liquidation_id", string="Attention orders", required=False
    )

    @api.depends(
        "invoice_liquidation_ids.total",
    )
    def _compute_amounts(self):
        for rec in self:
            rec.total_liquidation = sum(d.total for d in rec.invoice_liquidation_ids)

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        template_id = self.env["ir.model.data"].xmlid_to_res_id(
            "transmedical_proceso_base.medical_liquidation_mail_template", raise_if_not_found=False
        )
        lang = self.env.context.get("lang")
        template = self.env["mail.template"].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, "medical.liquidation", self.ids[0])
        ctx = {
            "default_model": "medical.liquidation",
            "default_res_id": self.ids[0],
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "mark_so_as_sent": True,
            "custom_layout": "mail.mail_notification_paynow",
            "force_email": True,
            "model_description": self.with_context(lang=lang).number,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

    @api.model
    def create(self, vals):
        vals.update({"number": self.env["ir.sequence"].next_by_code("medical.liquidation")})
        return super(MedicalLiquidation, self).create(vals)

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"ODA-{self.number}"

    def _compute_access_url(self):
        super(MedicalLiquidation, self)._compute_access_url()
        for liquidation_id in self:
            liquidation_id.access_url = "/my/medical_liquidation/%s" % (liquidation_id.id)


class MedicalLiquidationInvoice(models.Model):
    _name = "medical.liquidation.invoice"
    _description = "Medical liquidation invoice"

    liquidation_id = fields.Many2one(comodel_name="medical.liquidation", string="Liquidation", required=False)
    document_number = fields.Char(string="Document number", required=False)
    document_date = fields.Date(string="Document date", required=False)
    document_type = fields.Selection(
        string="Document type",
        selection=[
            ("sales_note", "Sales Note"),
            ("invoice", "Invoice"),
        ],
        required=False,
        default="invoice",
    )
    date_due = fields.Date(string="Date due", required=False)
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=False,
        domain=[("medical_service_provider", "=", True)],
    )
    sri_authorization = fields.Char(string="SRI Authorization", required=False)
    procedure_id = fields.Many2one(comodel_name="medical.procedure", string="Procedure", required=False)
    diagnostic_id = fields.Many2one(
        comodel_name="medical.diagnostic",
        string="Diagnostic",
        required=False,
        domain=[("procedure_id", "=", "procedure_id")],
    )
    quantity = fields.Float(string="Quantity", required=False, digits="Product Price")
    price_unit = fields.Float(string="Price unit", required=False)
    subtotal = fields.Float(string="Subtotal", compute="_compute_amount")
    not_covered = fields.Float(string="Not Covered", required=False)
    eligible = fields.Float(string="Eligible", compute="_compute_amount")
    deductible = fields.Float(string="Deductible", required=False)
    percentage = fields.Float(string="Percentage", required=False)
    total = fields.Float(string="Total", compute="_compute_amount")
    reason_not_covered = fields.Char(string="Reason not covered", required=False)
    not_covered_ids = fields.One2many(
        comodel_name="medical.liquidation.invoice.not.covered",
        inverse_name="invoice_id",
        string="Not covered detail",
        required=False,
    )
    beneficiary_type = fields.Selection(related="liquidation_id.beneficiary_type")

    @api.depends("price_unit", "quantity", "not_covered", "deductible", "percentage")
    def _compute_amount(self):
        for record in self:
            record.subtotal = record.price_unit * record.quantity
            record.eligible = record.price_unit - record.not_covered
            record.total = (record.eligible - record.deductible) - (
                ((record.eligible - record.deductible) * record.percentage) / 100
            )

    @api.constrains("date_due")
    def _constrains_invoive(self):
        for record in self:
            if record.date_due < record.document_date:
                raise UserError(_("The expiration date must be greater than the document date"))

    @api.constrains("document_number")
    def _constraint_unique_document_number(self):
        for record in self:
            liquidation_id = self.env["medical.liquidation.invoice"].search(
                [("document_number", "=", record.document_number), ("id", "!=", record.id)]
            )
            if liquidation_id:
                raise UserError(_("existing invoice in a previously created settlement"))


class MedicalLiquidationInvoiceNotCovered(models.Model):
    _name = "medical.liquidation.invoice.not.covered"
    _description = "Medical liquidation invoice not covered"

    invoice_id = fields.Many2one(comodel_name="medical.liquidation.invoice", string="Invoice", required=False)
    description = fields.Char(string="Description", required=False)
    amount = fields.Float(string="Amount", required=False)
