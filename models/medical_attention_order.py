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

    @api.model
    def create(self, vals):
        vals.update({
            'number': self.env['ir.sequence'].next_by_code('medical.attention.order')
        })
        return super(MedicalAttentionOrder, self).create(vals)
