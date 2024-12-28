from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.sql.expression import func
from dotenv import load_dotenv
import os
from functools import wraps


# .ENV IMPORT
load_dotenv()
API_KEY = os.getenv('API_KEY')



app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    
    

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "seats": self.seats,
            "has_toilet": self.has_toilet,
            "has_wifi": self.has_wifi,
            "has_sockets": self.has_sockets,
            "can_take_calls": self.can_take_calls,
            "coffee_price": self.coffee_price,
        }


with app.app_context():
    db.create_all()


#API KEY WRAPPER
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs)     :
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Unauthorized, invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function



#ROUTES
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods=['GET', 'POST'])
def random():
    random_cafe = Cafe.query.order_by(func.random()).first()

    if random_cafe:
        if request.method == 'POST' or request.is_json:
            return jsonify(random_cafe.to_dict())
        else:
            return render_template("index.html", cafe=random_cafe)
    else:
        return jsonify({"error": "No cafes available"}), 404
    

@app.route("/create", methods=['POST'])
def create_cafe():
    data = request.get_json()  
    
    
    name = data.get('name')
    map_url = data.get('map_url')
    img_url = data.get('img_url')
    location = data.get('location')
    seats = data.get('seats')
    has_toilet = data.get('has_toilet')
    has_wifi = data.get('has_wifi')
    has_sockets = data.get('has_sockets')
    can_take_calls = data.get('can_take_calls')
    coffee_price = data.get('coffee_price')

    new_cafe = Cafe(
        name=name,
        map_url=map_url,
        img_url=img_url,
        location=location,
        seats=seats,
        has_toilet=has_toilet,
        has_wifi=has_wifi,
        has_sockets=has_sockets,
        can_take_calls=can_take_calls,
        coffee_price=coffee_price
    )

    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(new_cafe.to_dict()), 201 
    
    

@app.route("/all",  methods=['GET', 'POST'])
def all():
    all_cafes = Cafe.query.all()
    
    if all_cafes:
        if request.method == 'POST' or request.is_json:
            return jsonify(all_cafes.to_dict())
        else:
            return render_template("index.html", cafes = all_cafes)
    else:
        return jsonify({"error": "No cafes available"}), 404
    
    
@app.route("/search", methods=['GET'])
def search():
    query_location = request.args.get('loc')

    if query_location:
        cafes = Cafe.query.filter(Cafe.location.ilike(f"%{query_location}%")).all()

        if cafes:
            return jsonify([cafe.to_dict() for cafe in cafes])
        else:
            return jsonify({"error": f"No cafes found in the location '{query_location}'"}), 404
    else:
        return jsonify({"error": "Location parameter 'loc' is required"}), 400
    
    
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)

    data = request.get_json()
    new_price = data.get('coffee_price')

    if new_price:
        cafe.coffee_price = new_price

        db.session.commit()

        return jsonify(cafe.to_dict()), 200
    else:
        return jsonify({"error": "New coffee price is required"}), 400
    
    
    
    
@app.route("/delete/<int:cafe_id>", methods=['DELETE'])
@require_api_key
def delete_cafe(cafe_id):
    return jsonify({"message": f"Cafe with id {cafe_id} has been deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
