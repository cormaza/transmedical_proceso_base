from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    medical_service_provider = fields.Boolean(string="Medical Service Provider", required=False)
    birth_date = fields.Date(string="Birth Date")
    age = fields.Integer(string="Age", compute="_compute_calculate_age")
    liquidation_ids = fields.One2many("medical.liquidation", "partner_id", string="Liquidaciones")
    count_liquidation = fields.Integer("Count Liquidation", compute="_compute_count_liquidation")
    relationship_id = fields.Many2one("medical.relationship", "Relationship")

    def action_show_liquidation_ids(self):
        self.ensure_one()
        tree_view = self.env.ref("transmedical_proceso_base.medical_liquidation_view_tree", raise_if_not_found=False)
        form_view = self.env.ref("transmedical_proceso_base.medical_liquidation_view_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Liquidation",
            "res_model": "medical.liquidation",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.liquidation_ids.ids)],
            "context": {"default_partner_id": self.id},
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action

    @api.depends("liquidation_ids")
    def _compute_count_liquidation(self):
        for rec in self:
            rec.count_liquidation = len(rec.liquidation_ids)

    @api.depends("birth_date")
    def _compute_calculate_age(self):
        for record in self:
            ahora = date.today()
            record.age = relativedelta(ahora, record.birth_date).years
