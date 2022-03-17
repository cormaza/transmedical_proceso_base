from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    medical_contract_id = fields.One2many(
        comodel_name="contract.contract", inverse_name="invoice_id", string="Contrato Medico", required=False
    )
    contract_count = fields.Integer(string="Contract Count", compute="_compute_count_contract")

    @api.depends("medical_contract_id")
    def _compute_count_contract(self):
        for record in self:
            record.contract_count = len(record.medical_contract_id.ids)

    def action_show_contract_ids(self):
        self.ensure_one()
        tree_view = self.env.ref("contract.contract_contract_tree_view", raise_if_not_found=False)
        form_view = self.env.ref("contract.contract_contract_form_view", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Contracts",
            "res_model": "contract.contract",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [("id", "in", self.medical_contract_id.ids)],
            "context": {"default_invoice_id": self.id},
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action
