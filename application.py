#!/usr/bin/env python3
#
# A web application that provides a list of items within a variety of
# categories as well as provide a user registration and authentication system

from flask import Flask, render_template, request, redirect, url_for
from flask import flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, User, Category, Item
# Create anti-forgery state token
from flask import session as login_session
import random
import string
# For Google OAuth 2.0
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


# Create a Flask instance with the name of the running application
app = Flask(__name__)
# Used by Flash message to create sessions for the users
app.secret_key = 'super_secret_key'
# Google OAuth 2.0
CLIENT_ID = json.loads(
    open('/var/www/catalog/client_secrets.json', 'r').read())['web']['client_id']

# Create session and connect to db
# engine = create_engine('sqlite:///itemcatalog.db',
#                        connect_args={'check_same_thread': False}, echo=True)
engine = create_engine('postgresql://catalog:catalog@localhost/itemcatalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Shows the categories and the latest items
@app.route('/')
@app.route('/categories')
def showCategories():
    """Shows the categories and the latest items"""

    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.id.desc()).limit(10)

    return render_template('categories.html', categories=categories,
                           items=items)

# Shows the items of a category
@app.route('/categories/<int:category_id>/')
@app.route('/categories/<int:category_id>/items/')
def showCategoryItems(category_id):
    """Shows the items of a category"""

    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).order_by(Item.title)

    return render_template('categoryItems.html', categories=categories,
                           category=category, items=items)


# Shows the information of an item
@app.route('/category/<int:category_id>/item/<int:item_id>/view',
           methods=['GET'])
def showItem(category_id, item_id):
    """Shows the information of an item"""

    item = session.query(Item).filter_by(id=item_id).one()
    creator = getUserInfo(item.user_id)

    return render_template('item.html', item=item, creator=creator)


# Adds a new item
@app.route('/category/item/new', methods=['GET', 'POST'])
def newItem():
    """Adds a new item"""

    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newItem = Item(title=request.form['name'],
                       description=request.form['description'],
                       category_id=request.form['category'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item Successfully Created: %s' % newItem.title)
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        return render_template('newItem.html', categories=categories)


# Edits an item
@app.route('/category/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """Edits an item"""

    if 'username' not in login_session:
        return redirect('/login')

    editedItem = session.query(Item).filter_by(id=item_id).one()
    if editedItem.user_id != login_session['user_id']:
        msgScript = "<script>function myFunction() {"
        msgScript += "alert('You are not authorized to edit this item. "
        msgScript += "Please create your own item in order to edit.');}"
        msgScript += "</script>"
        msgScript += "<body onload='myFunction()'>"
        return msgScript

    if request.method == 'POST':
        if request.form['name']:
            editedItem.title = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.category_id = request.form['category']

        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited: %s' % editedItem.title)
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        return render_template('editItem.html', categories=categories,
                               item=editedItem)


# Deletes an item
@app.route('/category/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """Deletes an item"""

    if 'username' not in login_session:
        return redirect('/login')

    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        msgScript = "<script>function myFunction() {"
        msgScript += "alert('You are not authorized to delete this item. "
        msgScript += "Please create your own item in order to delete.');}"
        msgScript += "</script>"
        msgScript += "<body onload='myFunction()'>"
        return msgScript

    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted: %s' % itemToDelete.title)
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


# Create anti-forgery state token to prevent request forgery
# Store it in the session for later validation
@app.route('/login')
def showLogin():
    """Shows login page"""

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


# Logs in using Google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Logs in using Google account"""

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads((h.request(url, 'GET')[1]).decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    return output


# Logs out from Google account
@app.route('/gdisconnect')
def gdisconnect():
    """Logs out from Google account"""

    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnects user based on provider
@app.route('/disconnect')
def disconnect():
    """Disconnects user based on provider"""

    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# Logs in using Facebook account
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Logs in using Facebook account"""

    # Verify the value of state to protect
    # against cross site reference forgery attacks
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data.decode('utf-8')

    # Exchange client token for long-lived server-side token
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token'
    url += '?grant_type=fb_exchange_token'
    url += '&client_id=%s' % app_id
    url += '&client_secret=%s' % app_secret
    url += '&fb_exchange_token=%s' % access_token
    h = httplib2.Http()
    result = (h.request(url, 'GET')[1]).decode('utf-8')

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server token exchange
        we have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value and replace the
        remaining quotes with nothing so that it can be used directly in the
        graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/me?access_token=%s' % token
    url += '&fields=name,id,email'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode('utf-8'))
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']

    login_session['facebook_id'] = data['id']
    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v3.2/me/picture?access_token=%s' % token
    url += '&redirect=0&height=200&width=200'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result.decode('utf-8'))

    login_session['picture'] = data['data']['url']

    # See if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# Logs in using Facebook account
@app.route('/fbdisconnect')
def fbdisconnect():
    """Logs in using Facebook account"""

    facebook_id = login_session['facebook_id']
    # The access token must be included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s' % facebook_id
    url += '/permissions?access_token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Creates a user
def createUser(login_session):
    """Creates a user"""

    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Gets user info based on user ID
def getUserInfo(user_id):
    """Gets user info based on user ID"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Gets user ID based on email
def getUserID(email):
    """Gets user ID based on email"""

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


# Returns JSON of all categories
@app.route('/categories/JSON')
def categoriesJSON():
    """Returns JSON of all categories"""
    categories = session.query(Category).all()
    return jsonify(Categories=[c.serialize for c in categories])


# Returns JSON of all items in a category
@app.route('/category/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    """Returns JSON of all items in a category"""
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


# Returns JSON of an item in a category
@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    """Returns JSON of an item in a category"""
    item = session.query(Item).filter_by(
        category_id=category_id, id=item_id).one()
    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    # Used by Flash message to create sessions for the users
    # app.secret_key = 'super_secret_key'
    # Enables the server to reload itself when it notices a code change
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
