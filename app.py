from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import products_functions as pf
import os
from dotenv import load_dotenv
import json

firebase_url = "https://preco-bom-ddcc1-default-rtdb.firebaseio.com/"
load_dotenv()
PRICE_ERROR = "PRICE_ERROR"
FIREBASECONFIG = os.getenv('FIREBASECONFIGS')

if not FIREBASECONFIG:
   load_dotenv(dotenv_path=os.path.abspath('/etc/secrets/'))

cred = credentials.Certificate(json.loads(FIREBASECONFIG))
firebase_admin.initialize_app(cred, {'databaseURL': firebase_url})

app = Flask(__name__)
CORS(app, resources={r'/products*': {'origins': '*'}})

@app.route("/products", methods=['GET'])
def get_products():
   return jsonify(db.reference('products').get())

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
   return jsonify(db.reference(f'products/{id}').get())

@app.route('/products', methods=['POST'])
def add_product():
   data = request.get_json()
   if data and 'id' in data:
      data['original_price'] = pf.get_product_price(data['url'])
      data['new_prices'] = [data['original_price']]
      data['new_prices_dates'] = [pf.get_current_date()]

      if data['original_price'] == PRICE_ERROR:
         return jsonify({"message": PRICE_ERROR}), 500

      try:
         ref = db.reference(f'products/{data["id"]}')
         ref.set(data)
         return jsonify({"message": "Product added successfully"}), 201
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
   print(data)
   if request.method == 'PUT':
      if data:
         try:
            ref = db.reference(f'products/{id}')
            product_data = ref.get()

            new_price = pf.get_product_price(product_data['url'])

            if new_price == PRICE_ERROR:
               print(PRICE_ERROR)
               response = jsonify({"message": "Product price not found", "product": data})
            elif new_price != data['new_prices'][-1]:
               data['new_prices'].append(float(new_price))
               data['new_prices_dates'].append(pf.get_current_date())
               response = jsonify({"message": "Product price updated successfully", "product": data})
            else:
               response = jsonify({"message": "Product updated successfully", "product": data})


            ref.update(data)

            # Set the CORS headers
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
            response.headers['Access-Control-Allow-Methods'] = 'PUT'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            response.status_code = 200

            return response
         except Exception as e:
            return jsonify({"message": f"Error updating product: {str(e)}"}), 500
      else:
         return jsonify({"message": "Invalid data"}), 400

@app.after_request
def after_request(response):
   if request.method == 'OPTIONS':
      response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
      response.headers['Access-Control-Allow-Methods'] = 'PUT, DELETE'
      response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
      response.status_code = 200
   return response

if __name__ == "__main__":
    app.run(debug=True)