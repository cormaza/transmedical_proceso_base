from odoo import fields, models, api


class MedicalBeneficts(models.Model):
    _name = 'medical.beneficts'
    _description = 'Beneficiaries'

    partner_id = fields.Many2one('res.partner', 'Beneficary')
    contract_id = fields.Many2one('contract.contract', 'Contrato')
    relationship_id = fields.Many2one('medical.relationship', 'Relationship')
