from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class MedicalAttentionOrder(models.Model):
    _name = "medical.attention.order"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "portal.mixin",
    ]
    _description = "Medical Attention Order"
    _rec_name = "number"

    number = fields.Char(string="Number", readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", default=lambda self: self.env.user.company_id
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    issue_date = fields.Datetime(string="Issue date", required=False, default=fields.Date.today())
    partner_id = fields.Many2one(related="contract_id.partner_id", store=True)
    beneficiary_id = fields.Many2one(comodel_name="res.partner", string="Beneficiary", required=True)
    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        required=True,
    )
    copay_percentage = fields.Float(related="contract_id.copay_percentage")
    contract_date = fields.Date("Contract Date", related="contract_id.date_start")
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
            ("liquidated", "Liquidated"),
            ("cancel", "Cancel"),
        ],
        required=False,
    )
    liquidation_id = fields.Many2one(comodel_name="medical.liquidation", string="Liquidation", required=False)
    attention_type = fields.Selection(
        string="Attention type",
        selection=[
            ("ambulatory", "Ambulatory"),
            ("hospitable", "Hospitable"),
        ],
        required=True,
        default="ambulatory",
    )
    ambulatory_attention_type = fields.Selection(
        string="Ambulatory Attention type",
        selection=[
            ("consult", "Consult"),
            ("images", "Images"),
            ("laboratory", "Laboratory"),
            ("procedure", "Procedure"),
        ],
        required=True,
        default="consult",
    )
    hospitable_attention_type = fields.Selection(
        string="Hospitable Attention type",
        selection=[
            ("images", "Images"),
            ("laboratory", "Laboratory"),
        ],
        required=True,
        default="images",
    )
    scheduled_date = fields.Date(string="Scheduled Date")
    concept = fields.Text(string="Concept", required=True)
    detail_ids = fields.One2many(
        comodel_name="medical.attention.order.detail", inverse_name="order_id", string="Details", required=False
    )
    subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_amounts",
        store=True,
    )
    copayment_total = fields.Monetary(
        string="CoPayment Total",
        compute="_compute_amounts",
        store=True,
    )

    @api.depends(
        "detail_ids.price_unit",
        "detail_ids.quantity",
        "detail_ids.copay",
    )
    def _compute_amounts(self):
        for rec in self:
            rec.subtotal = sum(d.quantity * d.price_unit for d in rec.detail_ids)
            rec.copayment_total = sum((d.quantity * d.price_unit * (d.copay / 100.0)) for d in rec.detail_ids)

    days_of_validity = fields.Integer(
        string="Days of validity",
        required=True,
        default=30,
    )
    due_date = fields.Date(
        string="Due date",
        compute="_compute_due_date",
        store=True,
    )

    @api.depends(
        "issue_date",
        "days_of_validity",
    )
    def _compute_due_date(self):
        for rec in self:
            rec.due_date = rec.issue_date and rec.issue_date + relativedelta(days=rec.days_of_validity)

    @api.model
    def create(self, vals):
        vals.update({"number": self.env["ir.sequence"].next_by_code("medical.attention.order")})
        return super(MedicalAttentionOrder, self).create(vals)

    @api.onchange("contract_id")
    def _onchange_contract(self):
        if self.contract_id:
            same_beneficiary = self.contract_id.partner_id.id in self.contract_id.beneficiary_ids.ids
            if self.contract_id.beneficiary_ids:
                if (len(self.contract_id.beneficiary_ids) - (same_beneficiary and 1 or 0)) == 1:
                    self.beneficiary_id = self.contract_id.beneficiary_ids.ids[0]
            else:
                self.beneficiary_id = self.partner_id.id

    beneficiary_domain_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Beneficiary_domain",
        compute="_compute_beneficiary_domain",
    )

    @api.depends(
        "contract_id",
    )
    def _compute_beneficiary_domain(self):
        for rec in self:
            partners = rec.contract_id and rec.contract_id.partner_id or self.env["res.partner"]
            if rec.contract_id.beneficiary_ids:
                partners |= rec.contract_id.mapped("beneficiary_ids.partner_id")
            rec.beneficiary_domain_ids = partners.ids

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        template_id = self.env["ir.model.data"].xmlid_to_res_id(
            "transmedical_proceso_base.medical_atencion_order_mail_template", raise_if_not_found=False
        )
        lang = self.env.context.get("lang")
        template = self.env["mail.template"].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, "medical.attention.order", self.ids[0])
        ctx = {
            "default_model": "medical.attention.order",
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

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"ODA-{self.number}"

    def _compute_access_url(self):
        super(MedicalAttentionOrder, self)._compute_access_url()
        for order_id in self:
            order_id.access_url = "/my/atention_order/%s" % (order_id.id)


class MedicalAttentionOrderDetail(models.Model):
    _name = "medical.attention.order.detail"
    _description = "Medical attention order detail"

    order_id = fields.Many2one(comodel_name="medical.attention.order", string="Order", required=False)
    currency_id = fields.Many2one(related="order_id.company_id.currency_id")
    description = fields.Char(string="Description", required=True)
    quantity = fields.Float(string="Quantity", required=False)
    price_unit = fields.Monetary(string="Price unit", required=False)
    subtotal = fields.Monetary(string="Subtotal", compute="_compute_amounts", store=True)
    diagnostic_id = fields.Many2one(comodel_name="medical.diagnostic", string="Diagnostic", required=False)
    copay = fields.Float(string="Copay(%)", compute="_compute_copay", store=True)
    eligible = fields.Monetary(string="Eligible", compute="_compute_amounts", store=True)
    total = fields.Monetary(string="Total", compute="_compute_amounts", store=True)

    @api.depends(
        "order_id.contract_id.copay_percentage",
        "order_id.state",
    )
    def _compute_copay(self):
        for rec in self:
            rec.copay = (
                rec.order_id.state not in ("approved", "liquidated")
                and rec.order_id.contract_id.copay_percentage
                or rec.copay
            )

    @api.depends(
        "price_unit",
        "quantity",
        "copay",
    )
    def _compute_amounts(self):
        for rec in self:
            rec.subtotal = rec.price_unit * rec.quantity
            rec.eligible = rec.subtotal * (1 - (rec.copay / 100.0))
            rec.total = rec.subtotal - rec.eligible
