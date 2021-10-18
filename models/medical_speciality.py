from odoo import api, fields, models
from odoo.osv import expression


class MedicalSpeciality(models.Model):

    _name = "medical.speciality"
    _description = "Medical Speciality"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    active = fields.Boolean(
        string="Active?",
        required=False,
        default=True,
        tracking=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        tracking=True,
    )
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )

    _sql_constraints = [("code_uniq", "unique(code)", "Medical diagnostic must have unique code")]

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("code", "=ilike", name + "%"), ("name", operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ["&"] + domain
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    def name_get(self):
        result = []
        for r in self:
            name = "{} - {}".format(r.code, r.name)
            result.append((r.id, name))
        return result
