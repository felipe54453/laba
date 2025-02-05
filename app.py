from flask import Flask, request, render_template_string, redirect, url_for
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

# In-memory store for all orders
ORDERS = []

# HTML template stored as a Python string for brevity
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Quick Order App</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; }
    .overdue { background-color: #ffcccc; }
    .order-list { margin-top: 1rem; }
    .order-list li { margin-bottom: 0.5rem; }
    .served { text-decoration: line-through; color: gray; }
  </style>
</head>
<body>
  <h1>Quick Order App</h1>

  <!-- Order Form -->
  <form method="POST" action="/">
    <label><strong>Customer Description:</strong></label><br>
    <input type="text" name="customerDescription" required placeholder="e.g., Woman in blue hat" />
    <br><br>

    <label><strong>Burger:</strong></label><br>
    <select name="mainItem">
      <option value="VERDADEIRINHO">Verdadeirinho</option>
      <option value="BACON">Bacon</option>
      <option value="SALADA">Salada</option>
    </select>
    <br><br>

    <label><strong>Modifications (hold CTRL or CMD to select multiple):</strong></label><br>
    <select name="modifications" multiple size="5">
      <option value="NO_CEBOLA">No Cebola</option>
      <option value="NO_MOSTARDA">No Mostarda</option>
      <option value="NO_KETCHUP">No Ketchup</option>
      <option value="SWAP_FALAFEL">Swap Falafel</option>
      <option value="SWAP_SHIMEJI">Swap Shimeji</option>
      <option value="ADD_BACON">Add Bacon</option>
      <option value="ADD_QUEIJO">Add Queijo</option>
      <!-- Extend as needed -->
    </select>
    <br><br>

    <label><strong>Sides (hold CTRL or CMD to select multiple):</strong></label><br>
    <select name="sides" multiple size="3">
      <option value="FRIES">Batata Frita</option>
      <option value="ONION_RINGS">Onion Rings</option>
      <option value="NUGGETS">Nuggets</option>
    </select>
    <br><br>

    <button type="submit">Place Order</button>
  </form>

  <hr>

  <!-- Active Orders -->
  <h2>Active Orders</h2>
  <ul class="order-list">
    {% for o in orders if not o.served %}
      {% set minutes_old = (now - o.timePlaced).total_seconds() / 60 %}
      <li class="
        {% if minutes_old >= 4 %}
          overdue
        {% endif %}
      ">
        <strong>{{ o.customerDescription }}</strong> —
        <em>{{ o.mainItem }}</em> |
        ({{ minutes_old|round(1) }} min)
        <form method="POST" action="{{ url_for('serve_order', order_id=o.id) }}" style="display:inline;">
          <button type="submit">Served</button>
        </form>
        <br>
        Modifications: {{ o.modifications }}
        <br>
        Sides: {{ o.sides }}
      </li>
    {% endfor %}
  </ul>

  <h2>Served Orders</h2>
  <ul class="order-list">
    {% for o in orders if o.served %}
      <li class="served">
        <strong>{{ o.customerDescription }}</strong> —
        <em>{{ o.mainItem }}</em>
      </li>
    {% endfor %}
  </ul>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    """
    - GET: Display existing orders and a form to create new orders.
    - POST: Create a new order (in memory) based on the form input.
    """
    if request.method == "POST":
        # Gather form data
        customer_description = request.form.get("customerDescription", "")
        main_item = request.form.get("mainItem", "")
        modifications = request.form.getlist("modifications")  # multiple select
        sides = request.form.getlist("sides")                  # multiple select

        # Create new order
        new_order = {
            "id": str(uuid.uuid4()),
            "customerDescription": customer_description,
            "mainItem": main_item,
            "modifications": modifications,
            "sides": sides,
            "timePlaced": datetime.now(),
            "served": False
        }
        ORDERS.append(new_order)

        # Redirect to home so refresh won't duplicate order
        return redirect(url_for("index"))

    # GET request: Render the main page
    return render_template_string(
        HTML_TEMPLATE,
        orders=ORDERS,
        now=datetime.now()
    )

@app.route("/serve/<order_id>", methods=["POST"])
def serve_order(order_id):
    """
    Marks a specific order as served.
    """
    for o in ORDERS:
        if o["id"] == order_id:
            o["served"] = True
            break
    return redirect(url_for("index"))

if __name__ == "__main__":
    # Run the app in debug mode, accessible at http://127.0.0.1:5000
    app.run(debug=True)
