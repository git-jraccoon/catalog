# Item Catalog Project

An application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Tech
- [Python], [SQLAlchemy], [Flask]
- [HTML], [JavaScript], [CSS]
- [jQuery], [AJAX]
- [OAuth 2.0]
- [SQLite]
- [VirtualBox]
- [Vagrant]
- [Linux VM]

## Start the virtual machine
- `cd` into the **vagrant** directory
- To start the virtual machine, run the command `vagrant up`
- To log in to the virtual machine, run the command `vagrant ssh`

## Set up the database
- `cd` into the **vagrant/catalog** directory
- To set up the database, run the command `python database_setup.py`
- To load the initial data, run the command `python database_load.py`

## Run the application
- `cd` into the **vagrant/catalog** directory
- To run the application, run the command `python application.py`
- To access the application, visit http://localhost:8000

## Functionalities
`/` or `/categories` - Shows the categories and the latest items

`/categories/<int:category_id>/` or `/categories/<int:category_id>/items/` - Shows the items of a category

`/category/<int:category_id>/item/<int:item_id>/view` - Shows the information of an item

`/category/item/new` - Adds a new item

`/category/<int:category_id>/item/<int:item_id>/edit` - Edits an item

`/category/<int:category_id>/item/<int:item_id>/delete` - Deletes an item

`/categories/JSON` - Returns JSON of all categories

`/category/<int:category_id>/items/JSON` - Returns JSON of all items in a category

`/category/<int:category_id>/item/<int:item_id>/JSON` - Returns JSON of an item in a category



[Python]: <https://www.python.org>
[SQLAlchemy]: <https://www.sqlalchemy.org/>
[Flask]: <http://flask.pocoo.org/>
[HTML]: https://html.com/>
[JavaScript]: <https://www.javascript.com/>
[CSS]: <https://developer.mozilla.org/en-US/docs/Web/CSS>
[jQuery]: <https://jquery.com/>
[AJAX]: <http://api.jquery.com/jquery.ajax/>
[OAuth 2.0]: <https://oauth.net/2/>
[SQLite]: <https://www.sqlite.org/index.html>
[VirtualBox]: <https://www.virtualbox.org>
[Vagrant]: <https://www.vagrantup.com>
[Linux VM]: <https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip>
