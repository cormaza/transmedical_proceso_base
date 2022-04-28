from odoo import fields, models


class MedicalProcedureType(models.Model):
    _name = "medical.procedure.type"
    _description = "Medical Type Procedure"

    code = fields.Char("Code", required=True)
    name = fields.Char("Name", required=True)
