import json
import math
from urllib.parse import parse_qs

from PIL.ImageChops import offset

from odoo import http
from odoo.http import request


def invalid_response(error,status):
    response_body={
        "error": error,
    }
    return request.make_json_response(response_body, status=status)

def valid_response(data,status,pagination_info):
    response_body={
        "message": "successful",
        "data":data,
    }
    if pagination_info:
        response_body['pagination_info']=pagination_info
    return request.make_json_response(response_body, status=status)

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
                return invalid_response("ID does not exist",status=400)
            return valid_response({
                "id":property_id.id,
                "name":property_id.name,
                "ref":property_id.ref,
                "description":property_id.description,
                "bedrooms":property_id.bedrooms,
                "postcode":property_id.postcode,
            },status=200)
        except Exception as error:
            return invalid_response(error,status=400)
    @http.route("/v1/properties",methods=["GET"],type="http",auth="none",csrf=False)
    def get_all_properties(self):
        try:
            params=parse_qs(request.httprequest.query_string.decode('utf-8'))
            property_domain=[]
            page= offset = None
            limit=5
            if params:
                if params.get('limit'):
                    limit = int(params.get('limit')[0])
                if params.get('page'):
                    page=int(params.get('page')[0])


            if page:
                offset=(page*limit) - limit
            if params.get('state'):
                property_domain+=[('state','=',params.get('state')[0])]
            property_ids=request.env['property'].sudo().search(property_domain,offset=offset,limit=limit,order="id desc")
            property_count=request.env['property'].sudo().search_count(property_domain)
            if not property_ids:
                return invalid_response("There is no records",status=400)

            return valid_response([{
                "id": prop.id,
                "name": prop.name,
                "ref": prop.ref,
                "description": prop.description,
                "bedrooms": prop.bedrooms,
            } for prop in property_ids],pagination_info={
                'page':page if page else 1,
                'limit':limit,
                'pages':math.ceil(property_count / limit) if limit else 1,
                'count':property_count
            }, status=200)

        except Exception as error:
            return invalid_response(error,status=400)

    @http.route("/v1/property/<int:property_id>",methods=["DELETE"],type="http",auth="none",csrf=False)
    def delete_property(self,property_id):
        try:
            property_id = request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return request.make_json_response("Id does not exist",status=400)
            property_id.unlink()
            return request.make_json_response({
                "message":"Property has been deleted",
            }, status=200)

        except Exception as error:
            return request.make_json_response(error,status=400)

