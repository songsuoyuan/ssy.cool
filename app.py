from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'no-secret-key'
app.config['MONGO_URI'] = 'mongodb://ssy:zhouzhou2013@localhost:27017/dota2'
app.config['JSON_AS_ASCII'] = False

bootstrap = Bootstrap(app)
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dota188')
def dota188():
    return render_template('dota188.html')

@app.route('/vpgame')
def vpgame():
    return render_template('vpgame.html')

@app.route('/slcsgo')
def slcsgo():
    return render_template('slcsgo.html')


@app.route('/api/dota188')
def api_dota188():
    db = mongo.db
    record = db.dota188.find({'latest':True}, {'_id':False,'name':True, 'price':True, 'timestamp':True},sort=[('price', -1)])
    result = list(record)
    name_to_c5_price = db.c5game.find({'latest':True}, {'_id':False,'name':True, 'price':True})
    name_to_c5_price_dict = {r['name']:r['price'] for r in name_to_c5_price}
    for r in result:
        if r['name'] in name_to_c5_price_dict:
            r['c5_price'] = round(name_to_c5_price_dict[r['name']], 2)
            r['rate'] = round(name_to_c5_price_dict[r['name']] / r['price'], 2)
        else:
            r['c5_price'] = None
            r['rate'] = None
        r['timestamp'] = r['timestamp'].strftime("%Y-%m-%d")
    return jsonify(result)

@app.route('/api/vpgame')
def api_vpgame():
    db = mongo.db
    record = db.vpgame.find({'latest':True}, {'_id':False,'name':True, 'price':True, 'timestamp':True},sort=[('price', -1)])
    result = list(record)
    name_to_c5_price = db.c5game.find({'latest':True}, {'_id':False,'name':True, 'price':True})
    name_to_c5_price_dict = {r['name']:r['price'] for r in name_to_c5_price}
    for r in result:
        if r['name'] in name_to_c5_price_dict:
            r['c5_price'] = round(name_to_c5_price_dict[r['name']], 2)
            r['rate'] = round(name_to_c5_price_dict[r['name']] / r['price'], 2)
        else:
            r['c5_price'] = None
            r['rate'] = None
        r['timestamp'] = r['timestamp'].strftime("%Y-%m-%d")
    return jsonify(result)

@app.route('/api/slcsgo')
def api_slcsgo():
    db = mongo.db
    record = db.slcsgo.find({'latest':True}, {'_id':False,'name':True, 'price':True, 'timestamp':True},sort=[('price', -1)])
    result = list(record)
    name_to_c5_price = db.c5game.find({'latest':True}, {'_id':False,'name':True, 'price':True})
    name_to_c5_price_dict = {r['name']:r['price'] for r in name_to_c5_price}
    for r in result:
        if r['name'] in name_to_c5_price_dict:
            r['c5_price'] = round(name_to_c5_price_dict[r['name']], 2)
            r['rate'] = round(name_to_c5_price_dict[r['name']] / r['price'], 2)
        else:
            r['c5_price'] = None
            r['rate'] = None
        r['timestamp'] = r['timestamp'].strftime("%Y-%m-%d")
    return jsonify([r for r in result if r['price'] > 20])

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=9999)
