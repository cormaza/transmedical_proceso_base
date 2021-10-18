from odoo import api, fields, models
from odoo.osv import expression


class MedicalProcedure(models.Model):

    _name = "medical.procedure"
    _description = "Medical Procedure"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    active = fields.Boolean(
        string="Active",
        required=False,
        default=True,
        tracking=True,
    )
    code = fields.Char(string="Procedure Code", required=True, tracking=True)
    name = fields.Char(string="Procedure Name", required=True, tracking=True)
    sex = fields.Selection(
        string="Sex",
        selection=[("male", "Male"), ("female", "Female"), ("any", "Any")],
        default="any",
        required=False,
    )
    min_age = fields.Integer(string="Min Age", required=False)
    max_age = fields.Integer(string="Max Age", required=False)

    _sql_constraints = [("code_uniq", "unique(code)", "Medical procedure must have unique code")]

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
