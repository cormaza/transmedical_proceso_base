from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    medical_service_provider = fields.Boolean(string="Medical Service Provider", required=False)
