from datetime import date

from odoo import fields, models


class MedicalBeneficts(models.Model):
    _name = "medical.beneficts"
    _description = "Beneficiaries"

    partner_id = fields.Many2one("res.partner", "Beneficary", required=True)
    contract_id = fields.Many2one("contract.contract", "Contrato", required=True, ondelete="cascade")
    relationship_id = fields.Many2one("medical.relationship", "Relationship", required=True)
    inclusion_date = fields.Date(string="Inclusion Date", default=date.today(), required=True)
