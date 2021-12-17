from odoo import models, fields


class ContractContract(models.Model):

    _inherit = "contract.contract"

    beneficiary_ids = fields.One2many("medical.beneficts", "contract_id", string="Beneficiaries")

    def name_get(self):
        result = []
        for rec in self:
            name = "{} - {}".format(rec.code, rec.name)
            result.append((rec.id, name))
        return result
