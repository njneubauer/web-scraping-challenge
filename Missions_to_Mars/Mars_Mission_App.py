from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

# initiate Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

@app.route("/")
def index(): 
    # Find data
    mars_update = mongo.db.collection.find_one()

    return render_template("index.html", mars=mars_update)

@app.route("/scrape")
def scrape():
    # call scrape function
    mars_data = scrape_mars.scrape()
    # Update monogo DB collection
    mongo.db.collection.update({}, mars_data, upsert=True)
    # Redirect back to index
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)