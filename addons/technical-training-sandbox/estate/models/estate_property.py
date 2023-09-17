from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import MissingError, ValidationError, AccessError


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = "id desc"

    name = fields.Char(string='Name', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', """Only one value can be defined for each given usage!"""),
    ]

    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    type_id = fields.Many2one('estate.property.type', string='Property Type')
    tag_ids = fields.Many2many('estate.property.tag', string='Property Tag')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    seller_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True,
                                default=lambda self: self.env.user)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(
        string='Available From',
        default=lambda self: (fields.Date.today() + timedelta(days=90)).strftime('%Y-%m-%d'),
        copy=False
    )
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='Garden Area (sqm)')
    total_area = fields.Integer(string='Total Area (sqm)', compute='compute_total_area')
    best_price = fields.Float(string='Best Offer', compute='compute_best_offer')
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection(
        string='Status',
        selection=[
            ('new', 'New'), ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'),
            ('canceled', 'Canceled')],
        default='new',
        copy=False)
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="This field is used to precise the orientation of the garden")

    @api.depends('living_area', 'garden_area')
    def compute_total_area(self):
        for line in self:
            line.total_area = line.living_area + line.garden_area

    @api.depends('offer_ids.price')
    def compute_best_offer(self):
        if self.offer_ids:
            self.best_price = max(self.offer_ids.mapped('price'))
        else:
            self.best_price = 0

    @api.onchange("garden")
    def _onchange_partner_id(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 10
        else:
            self.garden_orientation = False
            self.garden_area = 0

    def action_sold(self):
        if self.state == 'canceled':
            raise ValidationError("You can't sell a cancelled property")
        self.state = 'sold'

    def action_cancel(self):
        self.state = 'canceled'

    @api.constrains('expected_price')
    def _check_expected_price(self):
        for record in self:
            if record.expected_price < 0:
                raise ValidationError("You need a positive price")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.state = 'offer_accepted'
        return res

    def unlink(self):
        if self.state not in ['new', 'canceled']:
            raise ValidationError("It should not be possible to delete a property which is not new or canceled.")
        res = super(EstateProperty, self).unlink()
