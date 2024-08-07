from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import json
from decouple import config
import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(app_dir)
sys.path.append(project_dir)
from functions.products_functions import *

FIREBASE_URL = config('FIREBASE_URL')
PRICE_ERROR = "PRICE_ERROR"
FIREBASECONFIG = config('FIREBASECONFIG')
FLASK_ENV = config('FLASK_DEBUG')
PROD_URL = config('PROD_URL').split(',')

cred = credentials.Certificate(json.loads(FIREBASECONFIG))
firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

app = Flask(__name__)
CORS(app, resources={r'/products*': {'origins': '*'}})

@app.route("/data", methods=['GET'])
def get_data():
   return jsonify(db.reference().get())

@app.route("/products", methods=['GET'])
def get_products():
   return jsonify(db.reference('products').get())

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
   return jsonify(db.reference(f'products/{id}').get())

@app.route('/tags', methods=['GET'])
def get_tags():
   return jsonify(db.reference('tags').get())

@app.route('/products', methods=['POST'])
def add_product():
   data = request.get_json()
   if data:
      data['id'] = get_last_product_id(db.reference('products').get()) + 1
      data['available'] = True
      data['original_price'] = get_product_price(data['url'])
      data['new_prices'] = [data['original_price']]
      data['new_prices_dates'] = [get_current_date()]

      if data['original_price'] == PRICE_ERROR:
         return jsonify({"message": PRICE_ERROR}), 500

      try:
         ref = db.reference(f'products/{data["id"]}')
         ref.set(data)
         return jsonify({"message": "Product added successfully", "product": data}), 201
      except Exception as e:
         return jsonify({"message": f"Error adding product: {str(e)}"}), 500
   else:
      return jsonify({"message": "Invalid data"}), 400

@app.route('/products/edit/<int:id>', methods=['PUT', 'OPTIONS'])
def edit_product(id):
   data = request.get_json()

   if request.method == 'PUT':
      if data:
         try:
            ref = db.reference(f'products/{id}')
            ref.update(data)
            response = jsonify({"message": "Product price updated successfully", "product": data})

            # Set the CORS headers
            origin = request.headers.get('Origin')
            if FLASK_ENV == 'production':
               if origin in PROD_URL:
                  response.headers['Access-Control-Allow-Origin'] = origin
            else:
               response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            response.headers['Access-Control-Allow-Methods'] = 'PUT'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.status_code = 200

            return response
         except Exception as e:
            return jsonify({"message": f"Error updating product: {str(e)}"}), 500

@app.route('/products/update_price/<int:id>', methods=['PUT', 'OPTIONS'])
def update_product_price(id):
   data = request.get_json()
   print(data['name'])
   if request.method == 'PUT':
      if data:
         try:
            ref = db.reference(f'products/{id}')
            product_data = ref.get()

            new_price = get_product_price(product_data['url'])

            if new_price == PRODUCT_UNAVAILABLE:
               data['available'] = False
               response = jsonify({"message": "Product unavailable", "product": data})
               print("Product unavailable")
            elif new_price == PRICE_ERROR:
               data['available'] = False
               response = jsonify({"message": "Product price not found", "product": data})
               print("Price not found")
            elif new_price != data['new_prices'][-1]:
               data['available'] = True
               data['new_prices'].append(float(new_price))
               data['new_prices_dates'].append(get_current_date())
               response = jsonify({"message": "Product price updated successfully", "product": data})
               print("New price!")
            else:
               data['available'] = True
               response = jsonify({"message": "Product price did not change", "product": data})
               print("Same price!")

            ref.update(data)

            # Set the CORS headers
            origin = request.headers.get('Origin')
            if FLASK_ENV == 'production':
               if origin in PROD_URL:
                  response.headers['Access-Control-Allow-Origin'] = origin
            else:
               response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            response.headers['Access-Control-Allow-Methods'] = 'PUT'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.status_code = 200

            return response
         except Exception as e:
            return jsonify({"message": f"Error updating product: {str(e)}"}), 500
      else:
         return jsonify({"message": "Invalid data"}), 400

@app.route('/tags', methods=['POST'])
def add_tag():
   data = request.get_json()
   if data:
      try:
         ref = db.reference(f'tags/{data["id"]}')
         ref.set(data)
         return jsonify({"message": "Tag added successfully", "tag": data}), 201
      except Exception as e:
         return jsonify({"message": f"Error adding tag: {str(e)}"}), 500
   else:
      return jsonify({"message": "Invalid data"}), 400

@app.route('/tags/edit/<int:id>', methods=['PUT', 'OPTIONS'])
def edit_tag(id):
   data = request.get_json()

   if request.method == 'PUT':
      if data:
         try:
            ref = db.reference(f'tags/{id}')
            ref.update(data)
            response = jsonify({"message": "Tag edited successfully", "tag": data})

            # Set the CORS headers
            origin = request.headers.get('Origin')
            if FLASK_ENV == 'production':
               if origin in PROD_URL:
                  response.headers['Access-Control-Allow-Origin'] = origin
            else:
               response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            response.headers['Access-Control-Allow-Methods'] = 'PUT'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.status_code = 200

            return response
         except Exception as e:
            return jsonify({"message": f"Error editing tag: {str(e)}"}), 500

@app.after_request
def after_request(response):
   if request.method == 'OPTIONS' or request.method == 'POST':
      origin = request.headers.get('Origin')
      if FLASK_ENV == 'production':
         if origin in PROD_URL:
            response.headers['Access-Control-Allow-Origin'] = origin
      else:
         response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
   elif request.method == 'GET':
         response.headers.add("Access-Control-Allow-Origin", "*")
   response.headers['Access-Control-Allow-Methods'] = 'PUT, DELETE'
   response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
   response.status_code = 200
   return response

if __name__ == "__main__":
   app.run(debug=True)