from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# Routes for web interface

# Route for Landing Page
@app.route('/')
def landingPage():
    restaurants = session.query(Restaurant).all()
    return render_template('landingpage.htm',restaurants = restaurants)

# Route for adding new Restaurant
@app.route('/restaurant/new',methods=['GET','POST'])
def newRestaurant():
    if request.method == 'POST':
        newRestaurant = Restaurant(name = request.form['name'])
        session.add(newRestaurant)
        session.commit()
        print('NOVO RESTAURANTE ADICIONADO')
        return redirect(url_for('landingPage'))
    else:
        return render_template('newrestaurantform.htm')

# Route for deleting restaurant
@app.route('/restaurant/<int:restaurant_id>/delete', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
    restaurantDeleted = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantDeleted)
        session.commit()
        print("RESTAURANT DELETED")
        return redirect(url_for('landingPage'))
    else:
        return render_template('confirmdeleterestaurant.htm', restaurant = restaurantDeleted)

# Route for editing restaurant
@app.route('/restaurant/<int:restaurant_id>/edit', methods = ['GET','POST'])
def editRestaurant(restaurant_id):
    restaurantEdited = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        restaurantEdited.name = request.form['name']
        session.add(restaurantEdited)
        session.commit()
        return redirect(url_for('landingPage'))
    else:
        return render_template('editrestaurant.htm', restaurant = restaurantEdited)

# Route for showing a specific restaurant Menu
@app.route('/restaurant/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    
    return render_template('sublime_menu.htm',restaurant = restaurant, items = items)

# Route for adding a New MenuItem
@app.route('/restaurant/<int:restaurant_id>/new/', methods = ['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id, description = request.form['description'], price = request.form['price'], course = request.form['course'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.htm',  restaurant_id = restaurant_id)

# Route for editing a MenuItem
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods = ['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    menuitem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['name'] != '':
            menuitem.name = request.form['name']
        if request.form['description'] != '':
            menuitem.description = request.form['description']
        if request.form['price'] != '':
            menuitem.price = request.form['price']
        if request.form['course'] != '':
            menuitem.course = request.form['course']
        session.add(menuitem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.htm',restaurant_id = restaurant_id, menuitem = menuitem, menu_id = menu_id)

# Route for deleting a MenuItem
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    deletedmenu = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(deletedmenu)
        session.commit()
        flash('New Menu Item Created')
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:   
        return render_template('confirmdelete.htm', menuitem = deletedmenu, restaurant = restaurant)

# Routes for the API Siystem
@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return jsonify(MenuItems = [i.serializeMenu for i in items])

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def sendMenuItemJSON(restaurant_id,menu_id):
    menu = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(menu.serializeMenu)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port = 5000)
