from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import MissingError, ValidationError, AccessError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _order = "price desc"

    name = fields.Char(string='Name')
    property_id = fields.Many2one('estate.property', string='property', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    price = fields.Float(string='Price', required=True)
    status = fields.Selection(
        string='Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False)

    validity = fields.Integer(string='Validity (days)', default='7', compute="inverse_validity_duration",
                              inverse="compute_validity_duration", store=1)
    date_deadline = fields.Date(string='Deadline date', compute="compute_validity_duration",
                                inverse="inverse_validity_duration", store=1)

    @api.depends('property_id.create_date', 'validity', 'date_deadline')
    def compute_validity_duration(self):
        for record in self:
            if record.property_id:
                if record.property_id.create_date and record.validity:
                    record.date_deadline = record.property_id.create_date + timedelta(days=record.validity)

    def inverse_validity_duration(self):
        for record in self:
            if record.property_id:
                if record.date_deadline and record.property_id.create_date:
                    record.validity = (record.date_deadline - record.property_id.create_date.date()).days

    def action_accepted(self):
        if self.price < (self.property_id.expected_price * 0.9):
            raise ValidationError("The Offer price should be more than 90% of the expected price. ")
        self.status = 'accepted'
        self.property_id.buyer_id = self.partner_id.id
        self.property_id.selling_price = self.price
        self.property_id.state = 'offer_accepted'

    def action_refused(self):
        self.status = 'refused'
