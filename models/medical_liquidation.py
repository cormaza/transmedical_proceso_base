from odoo import fields, models


class MedicalLiquidation(models.Model):

    _name = "medical.liquidation"
    _description = "medical.liquidation"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
        "portal.mixin",
    ]
    _rec_name = "number"

    number = fields.Char(string="Number", required=False)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False)
    issue_date = fields.Datetime(string="Issue date", required=False)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=True)
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
    liquidation_type = fields.Selection(
        string="Liquidation type",
        selection=[
            ("personal", "Personal"),
            ("supplier", "Supplier"),
        ],
        required=True,
    )
