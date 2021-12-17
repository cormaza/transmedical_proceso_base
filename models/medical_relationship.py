from odoo import fields, models, api


class MedicalRelationShip(models.Model):
    _name = 'medical.relationship'
    _description = 'Description'

    code = fields.Char('Code', required=True)
    name = fields.Char('Description', required=True)
    short_name = fields.Char('Short Name', required=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Code must be unique!"),
    ]
