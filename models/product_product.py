from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.template"

    is_coverage = fields.Boolean(default=False, string="Is Corevarge?")
    type_coverage = fields.Selection(
        [
            ("only", "Holder only"),
            ("only+", "Holder + One"),
            ("only++", "Holder + Family"),
        ],
        string="Type Coverage",
    )
