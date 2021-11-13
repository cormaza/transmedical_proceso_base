from odoo import models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    def name_get(self):
        result = []
        for rec in self:
            name = "{} - {}".format(rec.code, rec.name)
            result.append((rec.id, name))
        return result
