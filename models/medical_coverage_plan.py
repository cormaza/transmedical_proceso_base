from odoo import fields, models


class MedicalCoveragePlan(models.Model):
    _name = "medical.coverage.plan"
    _description = "Medical Coverage Plan"

    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
    relationship_id = fields.Many2many(comodel_name="medical.relationship", string="Relationship")
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "Code must be unique!"),
    ]
