from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    bank_credit_card = fields.Many2one("account.type.credit.card", string="Bank Credit Card")
    number_credit_card = fields.Char("Number Credit Card")
    code_credit_card = fields.Char(string="Code Credit Card", max=4)
    type_credit_card = fields.Selection(
        [("debit", "Debit"), ("credit", "Credit")], string="Type Credit Card", default="debit"
    )
    type_res_bank = fields.Selection(
        [("card", "Card"), ("account", "Account")], string="Type Res Bank", default="account"
    )


class TypeCreditCard(models.Model):
    _name = "account.type.credit.card"

    name = fields.Char("Name", required=True)
    bank_id = fields.Many2one("res.bank", string="Bank")
