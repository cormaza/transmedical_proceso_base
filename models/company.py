from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    default_days_of_validity = fields.Integer(
        string="Days of validity", default=30, default_model="medical.attention.order"
    )
