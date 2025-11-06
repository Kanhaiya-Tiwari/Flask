from flask import Flask, request, jsonify, render_template, redirect
import os
import json

try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except Exception:
    MONGO_AVAILABLE = False

app = Flask(__name__)

# Try to use MongoDB if available and reachable; otherwise fallback to a local JSON file store.
use_mongo = False
coll = None
if MONGO_AVAILABLE:
    try:
        client = MongoClient(os.environ.get('MONGO_URI', 'mongodb://localhost:27017/'), serverSelectionTimeoutMS=2000)
        # force a server selection to detect unreachable server
        client.server_info()
        db = client['todo_db']
        coll = db['items']
        use_mongo = True
    except Exception:
        use_mongo = False

items_file = os.path.join(os.path.dirname(__file__), 'items.json')

def read_items():
    """Return list of todo items from Mongo or items.json."""
    if use_mongo and coll:
        docs = list(coll.find({}, {"_id": 0}))
        return docs
    # fallback to json file
    if not os.path.exists(items_file):
        with open(items_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    with open(items_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def add_item(doc):
    """Persist a new item into Mongo or the JSON file."""
    if use_mongo and coll:
        res = coll.insert_one(doc)
        return {"id": str(res.inserted_id)}
    items = read_items()
    items.append(doc)
    with open(items_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    return {"id": None}


@app.route('/')
def index():
    items = read_items()
    return render_template('todo.html', items=items, using_mongo=use_mongo)


@app.route('/submittodoitem', methods=['POST'])
def submittodoitem():
    itemName = request.form.get('itemName')
    itemDescription = request.form.get('itemDescription')
    if not itemName:
        return "itemName required", 400
    doc = {"itemName": itemName, "itemDescription": itemDescription}
    add_item(doc)
    return redirect('/')


if __name__ == '__main__':
    # Run on all network interfaces (0.0.0.0) on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)

