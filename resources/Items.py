import sqlite3
from flask import Request
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.items import ItemsModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help="This field can not be left blank"
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help="Every item needs a store id."
    )

    @jwt_required()
    def get(self, name):
        item = ItemsModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    def post(self, name):
        if ItemsModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists".format(name)}, 400
        data = Item.parser.parse_args()
        item = ItemsModel(name, **data)
        try:
            item.save_to_db()
        except Exception as e:
            return {'message': 'An error occurred inserting an item.'}, 500
        return item.json(), 201

    def delete(self, name):
        item = ItemsModel.find_by_name(name)
        if item:
            item.delete_from_db()
        else:
            return {'message': 'Item not found.'}, 404

        return {'message':'Item deleted'}

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemsModel.find_by_name(name)
        if item is None:
            item = ItemsModel(name, **data)
        else:
            item.price = data["price"]
        item.save_to_db()
        return item.json()



class ItemList(Resource):
    def get(self):
        return {"items": list(map(lambda x: x.json(), ItemsModel.query.all()))}
