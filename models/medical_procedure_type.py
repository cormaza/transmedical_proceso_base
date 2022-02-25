from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MedicalProcedureType(models.Model):
    _name = 'medical.procedure.type'
    _description = 'Medical Type Procedure'
    _rec_name = "display_name"

    code = fields.Char("Code")
    name = fields.Char("Name")
    display_name = fields.Char("Display Name", compute="_get_name_get")
    supplier_id = fields.Many2one(
        comodel_name='res.partner',
        string='Supplier',
        domain=[('medical_service_provider', '=', True)]
    )

    @api.depends("code", "supplier_id")
    def _get_name_get(self):
        for record in self:
            record.display_name = "{0} - {1}".format(
                record.name,
                record.supplier.name,
            )

    @api.constrains("code", "supplier_id")
    def _constraint_code(self):
        for record in self:
            if self.env['medical.procedure.type'].search([
                ('code', '=', record.code),
                ('supplier_id', '=', record.supplier_id.id),
                ('id', '!=', record.id)
            ]):
                raise UserError(_("Medical procedure type must have unique code"))
