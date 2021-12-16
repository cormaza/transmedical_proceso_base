from odoo import fields, models, api


class MedicalRelationShip(models.Model):
    _name = 'medical.relationship'
    _description = 'Description'

    code = fields.Char('Code')
    name = fields.Char('Description')
    short_name = fields.Char('Short Name')
