import json

from odoo import http
from odoo.http import request

class PropertyApi(http.Controller):


    @http.route("/v1/property", methods=["POST"], type="http", auth="none", csrf=False)
    def post_property(self):
        args=request.httprequest.data.decode()
        vals=json.loads(args)
        if not vals.get('name'):
            return request.make_json_response({
                "message": "Name is required!"
            }, status=400)
        try:
            res=request.env['property'].sudo().create(vals)
            if res:
                return request.make_json_response({
                    "message":"Property has been created",
                    "id":res.id,
                    "name":res.name
                },status=201)
        except Exception as error :
            return request.make_json_response({
                "message": error
            }, status=400)

    @http.route("/v1/property/json", methods=["POST"], type="json", auth="none", csrf=False)
    def post_property_json(self):
        args=request.httprequest.data.decode()
        vals=json.loads(args)
        res=request.env['property'].sudo().create(vals)
        if res:
            return [{
                "message": "Property has been created"
            }]

    @http.route("/v1/property/<int:property_id>",methods=["PUT"],type="http", auth="none",csrf=False)
    def update_property(self,property_id):
        try:
            property_id=request.env['property'].sudo().search([("id","=",property_id)])
            if not property_id:
                return request.make_json_response({
                    "message": "ID does not exist!"
                }, status=400)
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            property_id.write(vals)
            return request.make_json_response({
                "message": "Property has been updated successfully",
                "id": property_id.id,
                "name": property_id.name,
            }, status=201)
        except Exception as error:
            return request.make_json_response({
                "message": error
            }, status=400)

    @http.route("/v1/property/<int:property_id>",methods=["GET"],type="http",auth="none",csrf=False)
    def get_property(self,property_id):
        try:
            property_id=request.env['property'].sudo().search([('id','=',property_id)])
            if not property_id:
                return request.make_json_response({
                    "message":"ID does not exist",
                },status=400)
            return request.make_json_response({
                "id":property_id.id,
                "name":property_id.name,
                "ref":property_id.ref,
                "description":property_id.description,
                "bedrooms":property_id.bedrooms,
                "postcode":property_id.postcode,
            },status=200)
        except Exception as error:
            return request.make_json_response({
                "message":error,
            },status=400)
    @http.route("/v1/properties",methods=["GET"],type="http",auth="none",csrf=False)
    def get_all_properties(self):
        try:
            properties=request.env['property'].sudo().search([])
            data=[]
            for prop in properties:
                data.append({
                    "id":prop.id,
                    "name":prop.name,
                    "ref":prop.ref,
                    "description":prop.description,
                    "bedrooms":prop.bedrooms,
                    "postcode":prop.postcode,
                })
            return request.make_json_response({
                "count":len(data),
                "properties":data,
            },status=200)
        except Exception as error:
            return request.make_json_response({
                "message":str(error),
            },status=400)

