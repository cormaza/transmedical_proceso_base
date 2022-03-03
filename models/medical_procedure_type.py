from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MedicalProcedureType(models.Model):
    _name = 'medical.procedure.type'
    _description = 'Medical Type Procedure'

    code = fields.Char("Code")
    name = fields.Char("Name")
    supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
        domain=[('medical_service_provider', '=', True)]
    )

    def name_get(self):
        result = []
        for rec in self:
            name = "{} - {}".format(
                rec.name,
                rec.supplier_id.name,
            )
            result.append((rec.id, name))
        return result

    @api.constrains("code", "supplier_id")
    def _constraint_code(self):
        for record in self:
            if self.env['medical.procedure.type'].search([
                ('code', '=', record.code),
                ('supplier_id', '=', record.supplier_id.id),
                ('id', '!=', record.id)
            ]):
                raise UserError(_("Medical procedure type must have unique code"))
