from odoo import models, fields
from random import randint


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _order = "name"

    name = fields.Char(string='Name')

    def _default_color(self):
        return randint(1, 11)

    color = fields.Integer('Color', default=_default_color)
