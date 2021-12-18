from odoo import fields, models, api


class MedicalBeneficts(models.Model):
    _name = 'medical.beneficts'
    _description = 'Beneficiaries'

    partner_id = fields.Many2one('res.partner', 'Beneficary', required=True)
    contract_id = fields.Many2one('contract.contract', 'Contrato', required=True, ondelete="cascade")
    relationship_id = fields.Many2one('medical.relationship', 'Relationship', required=True)
