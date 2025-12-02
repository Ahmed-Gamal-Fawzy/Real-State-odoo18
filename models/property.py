from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class Property(models.Model):
    _name='property'
    _description='Property'
    _inherit = ['mail.thread','mail.activity.mixin']


    ref=fields.Char(default='New',readonly=1)
    name=fields.Char(required=True, default='New',size=4)
    description=fields.Text()
    postcode=fields.Char(required=True)
    date_availability=fields.Date(tracking=1)
    expected_selling_date=fields.Date(tracking=1)
    is_late=fields.Boolean()
    expected_price=fields.Float(digits=(0,5))
    selling_price=fields.Float()
    diff=fields.Float(compute='_compute_diff')
    bedrooms=fields.Integer(required=True)
    living_area=fields.Integer()
    facades=fields.Integer()
    garage=fields.Boolean()
    garden=fields.Boolean()
    garden_area=fields.Integer()
    garden_orientation=fields.Selection([
        ('north','North'),
        ('south','South'),
        ('east','East'),
        ('west','West'),
    ],default='north')
    owner_id = fields.Many2one('owner')
    tag_ids=fields.Many2many('tag')
    owner_address=fields.Char(related='owner_id.address',readonly=0,store=1)
    owner_phone=fields.Char(related='owner_id.phone',readonly=0,store=1)
    create_time=fields.Datetime(default=fields.Datetime.now())
    next_time=fields.Datetime(compute='_compute_next_time')

    state=fields.Selection([
        ('draft','Draft'),
        ('pending','Pending'),
        ('sold','Sold'),
        ('closed','Closed'),
    ],default='draft')

    _sql_constraints = [
        ('unique_name','unique("name")','This name is exist!')
    ]

    line_ids=fields.One2many('property.line','property_id')
    active=fields.Boolean(default=True)

    @api.depends('create_time')
    def _compute_next_time(self):
        for rec in self:
            if rec .create_time:
                rec.next_time=rec.create_time+ timedelta(hours=6)
            else:
                rec.next_time=False

    @api.depends('expected_price','selling_price','owner_id.phone')
    def _compute_diff(self):
        for rec in self:
            rec.diff=rec.expected_price-rec.selling_price

    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        for rec in self:
            print("inside _onchange_expected_price")
            return {
                'warning':{'title':'warning','message':'negative value','type':'notification'}
            }

    @api.constrains('bedrooms')
    def _check_bedrooms_greater_zero(self):
        for rec in self:
            if rec.bedrooms==0:
                raise ValidationError('Please add valid number of bedrooms')


    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state,'draft')
            print("inside action_draft")
            rec.state='draft'


    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending')
            rec.write({
                'state':'pending'
            })

    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold')
            rec.state='sold'
    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state='closed'

    def check_expected_selling_date(self):
        property_ids=self.search([])
        for rec in property_ids:
            if rec.expected_selling_date and rec.expected_selling_date < fields.Date.today():
                rec.is_late=True


    def action(self):
        print(self.env['property'].search(['|',('name','=','New6'),('postcode','!=','2020')]))

    @api.model
    def create(self, vals):
        if vals.get('ref') == 'New' or not vals.get('ref'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('property_seq')
        return super(Property, self).create(vals)

    def create_history_record(self,old_state,new_state,reason=""):
        for rec in self:
            rec.env['property.history'].create({
                'user_id':rec.env.uid,
                'property_id':rec.id,
                'old_state':old_state,
                'new_state':new_state,
                'reason':reason or "",
                'line_ids':[(0,0,{'description':line.description,'area':line.area}) for line in rec.line_ids],
            })

    def action_open_change_state_wizard(self):
        action=self.env['ir.actions.actions']._for_xml_id('app_one1.change_state_wizard_action')
        action['context']={'default_property_id':self.id}
        return action

    def action_open_related_owner(self):
        action=self.env['ir.actions.actions']._for_xml_id('app_one1.owner_action')
        view_id=self.env.ref('app_one1.owner_view_form').id
        action['res_id']=self.owner_id.id
        action['views']=[[view_id,'form']]
        return action

class PropertyLines(models.Model):
    _name="property.line"

    property_id=fields.Many2one('property')
    area=fields.Float()
    description=fields.Char()