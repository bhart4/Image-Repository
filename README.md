# image-repository

This is **Bridget Hart**'s submission to the **Shopify 2021 Winter Developer Challenge**. :-)

Here is a Marketplace where users can view and buy products!
The administrator can add and restock inventory using the Developer Tool.

This project has been implemented in Python using _Flask_ to serve a web interface
and _sqlite3_ to track product information and transactions. 

## Usage

To use this application, run `python3 server.py` from the command line.
This will create the appropriate database tables and start the Flask server.

After this, open a web browser at the address given by Flask (usually http://127.0.0.1:5000).
The application shows a listing of each product with its image, name, and price.

Users have the option to BUY available inventory. This will verify that there is enough
stock, record the transaction info in the database, and decrement inventory appropriately.

All of the displayed products retrieve data directly from a database table and are 
generated live with an HTML template. The images themselves are served from a static images folder.

Use the Developer Tool to add new products and add additional stock for existing products. 
When adding new inventory, images are added to the static images folder and database.

## Next Steps

A beautiful **UI** for both the Marketplace and Dev Tool.

The ability to **delete** images from the UI and also from the static images folder.
Implemented in a similar manner to the current add functionality.

**Access control** that requires Users and Developers to login before using the app.
This will involve a POST request with valid credentials to a /login endpoint.
Users can then login and save items to a wish list and cart for later checkout, and save payment 
information to make purchases easy!
Developers can login to access the Developer Tool in order to add/restock/delete inventory.

