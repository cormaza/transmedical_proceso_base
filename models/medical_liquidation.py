from odoo import fields, models, api, _


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
    issue_date = fields.Datetime(string="Issue date", required=False)
    reception_date = fields.Date(
        string='Reception date',
        required=False,
        default=fields.Date.today(),
    )
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
            ("done", "Approved"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
    )
    beneficiary_type = fields.Selection(
        string="Beneficiary type",
        selection=[
            ("personal", "Personal"),
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
    concept = fields.Text(
        string="Concept",
        required=False
    )
    invoice_liquidation_ids = fields.One2many(
        comodel_name='medical.liquidation.invoice',
        inverse_name='liquidation_id',
        string='Invoices liquidation',
        required=False
    )
    max_payment_date = fields.Date(
        string='Max payment date',
        required=False
    )
    total_liquidation = fields.Float(
        string='Total liquidation',
        required=False
    )
    attention_order_ids = fields.One2many(
        comodel_name='medical.attention.order',
        inverse_name='liquidation_id',
        string='Attention orders',
        required=False
    )

    @api.model
    def create(self, vals):
        vals.update({
            'number': self.env['ir.sequence'].next_by_code('medical.liquidation')
        })
        return super(MedicalLiquidation, self).create(vals)

class MedicalLiquidationInvoice(models.Model):

    _name = 'medical.liquidation.invoice'
    _description = 'Medical liquidation invoice'

    liquidation_id = fields.Many2one(
        comodel_name='medical.liquidation',
        string='Liquidation',
        required=False)
    document_number = fields.Char(
        string='Document number',
        required=False
    )
    document_date = fields.Date(
        string='Document date',
        required=False
    )
    document_type = fields.Selection(
        string='Document type',
        selection=[
            ('sales_note', 'Sales Note'),
            ('invoice', 'Invoice'),
        ],
        required=False,
        default='invoice'
    )
    date_due = fields.Date(
        string='Date due',
        required=False
    )
    supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
        required=False
    )
    sri_authorization = fields.Char(
        string='SRI Authorization',
        required=False
    )
    procedure_id = fields.Many2one(
        comodel_name='medical.procedure',
        string='Procedure',
        required=False
    )
    diagnostic_id = fields.Many2one(
        comodel_name='medical.diagnostic',
        string='Diagnostic',
        required=False
    )
    quantity = fields.Float(
        string='Quantity',
        required=False
    )
    price_unit = fields.Float(
        string='Price unit',
        required=False
    )
    subtotal = fields.Float(
        string='Subtotal',
        required=False
    )
    not_covered = fields.Float(
        string='Not Covered',
        required=False
    )
    eligible = fields.Float(
        string='Eligible',
        required=False
    )
    deductible = fields.Float(
        string='Deductible',
        required=False
    )
    percentage = fields.Float(
        string='Percentage',
        required=False
    )
    total = fields.Float(
        string='Total',
        required=False
    )
    reason_not_covered = fields.Char(
        string='Reason not covered',
        required=False)
    not_covered_ids = fields.One2many(
        comodel_name='medical.liquidation.invoice.not.covered',
        inverse_name='invoice_id',
        string='Not covered detail',
        required=False
    )
    beneficiary_type = fields.Selection(related="liquidation_id.beneficiary_type")


class MedicalLiquidationInvoiceNotCovered(models.Model):

    _name = 'medical.liquidation.invoice.not.covered'
    _description = 'Medical liquidation invoice not covered'

    invoice_id = fields.Many2one(
        comodel_name='medical.liquidation.invoice',
        string='Invoice',
        required=False
    )
    description = fields.Char(
        string='Description',
        required=False
    )
    amount = fields.Float(
        string='Amount',
        required=False
    )
