from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _order = "name"

    name = fields.Char(string='Name')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")

    property_ids = fields.One2many('estate.property', 'type_id')
