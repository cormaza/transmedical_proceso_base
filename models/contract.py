from odoo import fields, models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    beneficiary_ids = fields.One2many("medical.beneficts", "contract_id", string="Beneficiaries")
    copay_percentage = fields.Float(
        string="Copay %",
        required=True,
        default=20,
    )

    def name_get(self):
        result = []
        for rec in self:
            name = "{} - {}".format(rec.code, rec.name)
            result.append((rec.id, name))
        return result
