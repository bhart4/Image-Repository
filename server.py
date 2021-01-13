from flask import Flask, render_template, request
import sqlite3 as sql
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_cursor():
    conn = sql.connect("database.db")
    cur = conn.cursor()
    return (cur, conn)

# Initialize the sqlite database and create tables for inventory and transactions
def initialize_db():
    (cur, conn) = get_cursor()

    # Create table to hold inventory
    cur.execute("DROP TABLE IF EXISTS inventory")
    cur.execute("CREATE TABLE inventory (name TEXT, imgpath TEXT, price INTEGER, stock INTEGER)")

    # Create table to hold transactions
    cur.execute("DROP TABLE IF EXISTS transactions")
    cur.execute("CREATE TABLE transactions (timestamp TEXT, productid INTEGER, value INTEGER)")
    
    # Commit the db changes
    conn.commit()
    print("Initialized database")

@app.route("/devtool")
def dev_tool():
    (cur, _) = get_cursor()
    cur.execute("SELECT rowid, * FROM inventory")
    
    rows = cur.fetchall()
    print("Retrieved %d database entries" % len(rows))
    
    # Pre-process inventory info for HTML template
    inventory = []
    for row in rows:
        inventory.append({
            "id":    row[0],
            "name":  row[1],
            "src":   "/static/%s" % (row[2]),
            "price": "$%.2f" % (row[3]),
            "stock": "%d left" % (row[4]),
        })
    
    # Display total sales
    cur.execute("SELECT SUM(value) FROM transactions")
    result = cur.fetchone()[0]
    earnings = result if result else 0

    return render_template("devtool.html", inventory=inventory, earnings=earnings)

@app.route("/add", methods=['GET', 'POST'])
def add_inventory():
    if request.method == 'GET':
        return render_template("add.html")
    else:
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        fileName = 'images/'+file.filename

        (cur, conn) = get_cursor()
        cur.execute("INSERT INTO inventory (name, imgpath, price, stock) VALUES (?,?,?,?)", (name, fileName, price, stock))
        conn.commit()
        return render_template("messagedev.html", message="Successfully added new inventory!")

@app.route("/")
def marketplace():
    (cur, _) = get_cursor()
    cur.execute("SELECT rowid, * FROM inventory")
    
    rows = cur.fetchall()
    print("Retrieved %d database entries" % len(rows))
    
    # Pre-process inventory info for HTML template
    inventory = []
    for row in rows:
        inventory.append({
            "id":    row[0],
            "name":  row[1],
            "src":   "/static/%s" % (row[2]),
            "price": "$%.2f" % (row[3]),
        })

    return render_template("index.html", inventory=inventory)

@app.route("/buy/<product_id>")
def buy(product_id):
    if not product_id:
        return render_template("message.html", message="Invalid product ID!")

    (cur, conn) = get_cursor()

    cur.execute("SELECT rowid, price, stock FROM inventory WHERE rowid = ?", (product_id,))
    result = cur.fetchone()

    if not result:
        return render_template("message.html", message="Invalid product ID!")
    (rowid, price, stock) = result

    if stock <= 0:
        return render_template("message.html", message="Insufficient stock!")

    print("Processed transaction of value $%.2f" % (price/100.0))
    cur.execute("INSERT INTO transactions (timestamp, productid, value) VALUES " + \
        "(datetime(), ?, ?)", (rowid, price))

    cur.execute("UPDATE inventory SET stock = stock - 1 WHERE rowid = ?", (product_id,))
    conn.commit()
    return render_template("message.html", message="Purchase successful!")

@app.route("/restock/<product_id>", methods=['GET', 'POST'])
def restock(product_id):
    if request.method == 'GET':
        return render_template("restock.html")
    else:
        if not product_id:
            return render_template("message.html", message="Invalid product ID!")

        (cur, conn) = get_cursor()

        cur.execute("SELECT rowid, price, stock FROM inventory WHERE rowid = ?", (product_id,))
        result = cur.fetchone()

        if not result:
            return render_template("message.html", message="Invalid product ID!")
        (rowid, price, stock) = result

        restock = request.form['restock']

        cur.execute("UPDATE inventory SET stock = stock + ? WHERE rowid = ?", (restock, product_id,))
        conn.commit()
        return render_template("messagedev.html", message="Restock successful!")

@app.route("/reset")
def reset():
    initialize_db()
    return render_template("messagedev.html", message="Inventory reset.")

if __name__ == '__main__':
    initialize_db()
    app.run(debug = True)