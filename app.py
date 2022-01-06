import time
import requests

from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = 'no-secret-key'
app.config['MONGO_URI'] = 'mongodb://admin:password@localhost:27017/'
app.config['MONGO_AUTH_SOURCE'] = 'admin'
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


bootstrap = Bootstrap(app)
base_mongodb = PyMongo(app)
mongo = base_mongodb.cx['dota2']
mongo_csgo = base_mongodb.cx['csgo']
mongo_bdwm = base_mongodb.cx['bdwm']


header_vp = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
    'Host':'www.vpgame.com',
    'Referer': 'https://www.vpgame.com/prediction',
    'Connection':'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,es;q=0.2',
    'Cookie': 'VPLang=zh_CN; VPLang.sig=YnJ5rF9PQgOnWLVHGcoeKlgoy3E; VPTimeZone=Asia%2FChongqing; VPSiteGame.sig=wpEogptRBDmjX9j5f6ccOdf1BIk; VPSiteGame=dota'
}

header_5e = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36',
    'Host':'www.dota188.com',
    'Referer': 'https://www.dota188.com/',
    'Connection':'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,es;q=0.2',
    'Cookie': 'locale=zh_CN'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crawl_stats')
def crawl():
    return jsonify(mongo_bdwm.command("collstats", "content"))

@app.route('/crawl_latest')
def craw_latest():
    db = mongo_bdwm
    res = list(db.content.find({}, {'_id':False}).sort('timestamp', -1).limit(10))
    return jsonify(res)

@app.route('/dota188')
def dota188():
    return render_template('dota188.html')

@app.route('/vpgame')
def vpgame():
    return render_template('vpgame.html')

@app.route('/slcsgo')
def slcsgo():
    return render_template('slcsgo.html')

@app.route('/diamond')
def diamond():
    return render_template('diamond.html')

@app.route('/ingot')
def ingot():
    return render_template('ingot.html')

@app.route('/csgo_dota188')
def csgo_dota188():
    return render_template('csgo_dota188.html')

@app.route('/api/csgo_dota188')
def api_csgo_dota188():
    db = mongo_csgo
    aggregation_string=[{"$group" : {"_id" : "$name", "timestamp":{ "$last": "$timestamp" }, "price":{ "$last": "$price" }, "latest":{ "$last": "$latest" }}}, {"$sort":{"price": -1}}]
    record = db.dota188.aggregate(aggregation_string)
    result = list(record)
    for r in result:
        r['reliable'] = '高' if r['latest'] else '低'
        r['timestamp'] = r['timestamp'].strftime("%Y-%m-%d")
    return jsonify(result)

@app.route('/api/dota188')
def api_dota188():
    db = mongo
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
    db = mongo
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
    db = mongo
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

@app.route('/api/diamond')
def api_diamond():
    db = mongo
    name_to_c5_price = db.c5game.find({'latest':True}, {'_id':False,'name':True, 'price':True})
    name_to_c5_price_dict = {r['name']:r['price'] for r in name_to_c5_price}
    api_url = 'https://www.vpgame.com/market/gift/api/mall/list?limit=100&offset=0&appid=570&order_type=pro_price&order=desc&t=1589388518670'
    res = requests.get(api_url, headers=header_vp, timeout=30)
    if res.status_code == 200:
        result = res.json().get('data')
    else:
        return None
    list_result = []
    for r in result:
        item = r['item']
        name = item['name']
        price = float(item['diamond'])
        if price < 5:
            break
        if name in name_to_c5_price_dict:
            c5_price = round(name_to_c5_price_dict[name], 2)
            rate = round(name_to_c5_price_dict[name] / price, 2)
        else:
            c5_price = None
            rate = None
        inventory= r['inventory']
        list_result.append({'name':name, 'price':price, 'c5_price':c5_price, 'rate':rate, 'inventory':inventory})
    return jsonify(list_result)

@app.route('/api/ingot')
def api_ingot():
    db = mongo
    name_to_c5_price = db.c5game.find({'latest':True}, {'_id':False,'name':True, 'price':True})
    name_to_c5_price_dict = {r['name']:r['price'] for r in name_to_c5_price}
    api_url = 'https://www.dota188.com/api/ingotitems/v2/list.do?rel=goldingot_items&itemWidth=160&data=loading&page=1&total=164&pages=3&_=1546271685565'
    res = requests.get(api_url, headers=header_5e, timeout=30)
    if res.status_code == 200:
        result = res.json().get('datas').get('list')
    else:
        return None
    list_result = []
    for item in result:
        name = item['name']
        quality = item['quality']['tag']
        price = float(item['value'])
        if price < 5:
            break
        if quality:
            name = quality + ' ' + name
        if name in name_to_c5_price_dict:
            c5_price = round(name_to_c5_price_dict[name], 2)
            rate = round(name_to_c5_price_dict[name] / price, 2)
        else:
            c5_price = None
            rate = None
        inventory= item['num']
        list_result.append({'name':name, 'price':price, 'c5_price':c5_price, 'rate':rate, 'inventory':inventory})
    return jsonify(list_result)


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=9999)
