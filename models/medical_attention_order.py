from odoo import fields, models, api, _


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
    issue_date = fields.Datetime(string="Issue date", required=False)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True)
    contract_id = fields.Many2one(
        comodel_name='contract.contract',
        string='Contract',
        required=False
    )
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
        default="ambulatory"
    )
    ambulatory_attention_type = fields.Selection(
        string='Ambulatory Attention type',
        selection=[
            ('consult', 'Consult'),
            ('images', 'Images'),
            ('laboratory', 'Laboratory'),
            ('procedure', 'Procedure'),
        ],
        required=True,
        default="consult"
    )
    hospitable_attention_type = fields.Selection(
        string='Hospitable Attention type',
        selection=[
            ('images', 'Images'),
            ('laboratory', 'Laboratory'),
        ],
        required=True,
        default="images"
    )
    concept = fields.Text(
        string='Concept',
        required=True
    )
    detail_ids = fields.One2many(
        comodel_name='medical.attention.order.detail',
        inverse_name='order_id',
        string='Details',
        required=False
    )
    subtotal = fields.Float(
        string='Subtotal',
        required=False
    )
    copayment_percentage = fields.Float(
        string='CoPayment Percentage',
        required=False
    )
    copayment_total = fields.Float(
        string='CoPayment Total',
        required=False
    )

    @api.model
    def create(self, vals):
        vals.update({
            'number': self.env['ir.sequence'].next_by_code('medical.attention.order')
        })
        return super(MedicalAttentionOrder, self).create(vals)


class MedicalAttentionOrderDetail(models.Model):

    _name = "medical.attention.order.detail"
    _description = 'Medical attention order detail'

    order_id = fields.Many2one(
        comodel_name='medical.attention.order',
        string='Order',
        required=False
    )
    description = fields.Char(
        string='Description',
        required=True
    )
    quantity = fields.Float(
        string='Quantity',
        required=False
    )
    price_unit = fields.Float(
        string='Price unit',
        required=False
    )
    diagnostic_id = fields.Many2one(
        comodel_name='medical.diagnostic',
        string='Diagnostic',
        required=False
    )
    eligible = fields.Float(
        string='Eligible',
        required=False
    )
    total = fields.Float(
        string='Total',
        required=False
    )
