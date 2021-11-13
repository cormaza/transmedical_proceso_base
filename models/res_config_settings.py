from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    default_days_of_validity = fields.Integer(related="company_id.default_days_of_validity", readonly=False)
