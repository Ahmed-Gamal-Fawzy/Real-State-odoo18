from odoo.tests.common import TransactionCase
from odoo import fields

class TestProperty(TransactionCase):

    def setUp(self,*args,**kwargs):
        super(TestProperty,self).setUp()

        self.property_01_record=self.env['property'].create({
            'ref':'PRT1000',
            'name':'New 1000',
            'description':'New 1000 description',
            'postcode':'100100',
            'date_availability':fields.Date.today(),
            'bedrooms':10,
            'expected_price':10000,
        })

    def test_01_property_values(self):
        property_id=self.property_01_record
        self.assertRecordValues(property_id,[{
            'ref': 'PRT1000',
            'name': 'New 1000',
            'description': 'New 1000 description',
            'postcode': '100100',
            'date_availability': fields.Date.today(),
            'bedrooms': 10,
            'expected_price': 10000,
        }])