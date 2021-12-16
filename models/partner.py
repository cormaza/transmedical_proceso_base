from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    medical_service_provider = fields.Boolean(string="Medical Service Provider", required=False)
    contract_id = fields.Many2one(comodel_name="contract.contract", string="Contract")
