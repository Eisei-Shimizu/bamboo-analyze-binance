import sys
sys.path.append('/home/ec2-user/.local/lib/python3.7/site-packages')
from binance.client import Client
import json
import time
import math
import logging
from logging.handlers import RotatingFileHandler
import datetime
from const import Const
from aggregate import Aggregate
import urllib.request
import urllib.parse

def save_all_price(symbol):
    
    res_all_price = None
    try:
        res_all_price = client.get_all_tickers()
    except Exception as  e:
        logging.error(e)
    
    if res_all_price != None:
        save_list = []
        for item in res_all_price:
            if symbol in item["symbol"] and check_ng_word(item["symbol"]):
                save_list.append(item)
        
        write_all_price(save_list)
        
    else:
        logging.error("全銘柄の価格取得に失敗")

def check_ng_word(word):
    return "UP" not in word and "DOWN" not in word and "BULL" not in word and "BEAR" not in word


def write_all_price(all_price):
    logging.info("全銘柄の価格を外部ファイルに保存")

    try:
        file = open(Const.ALL_PRICE_SAVE_FILE_PATH, 'w')
        file.write(json.dumps({'all_price': all_price}))
        logging.info("全銘柄の価格保存に成功しました")
    except Exception as e:
        logging.error(e)
    finally:
        file.close()

def get_all_price_from_save_file():
    logging.info("全銘柄の価格を外部ファイルから取得")
    all_price = []
    file = None

    try:
        file = open(Const.ALL_PRICE_SAVE_FILE_PATH)
        all_price_data = file.read()
        logging.info(all_price_data)
        all_price = json.loads(all_price_data)["all_price"]
    except Exception as e:
        logging.error(e)
    finally:
        if file != None:
            file.close()
    
    return all_price

def add_all_price(symbol):
    logging.info("価格チェック銘柄に追加")
    all_price = get_all_price_from_save_file()
    all_price.append(symbol)
    write_all_price(all_price)

def write_detectioned_symbol(detectioned_symbol, detection_price_rise_rate):
    logging.info("検出済銘柄の価格を外部ファイルに保存")
    detection_price_rise_rate_formated = int(detection_price_rise_rate * 100)
    file_path = Const.DETECTIONED_SYMBOL_SAVE_FILE_PATH + "_" + str(detection_price_rise_rate_formated) + "_" + base_symbol + Const.FILE_TYPE_JSON

    try:
        file = open(file_path, 'w')
        file.write(json.dumps({'detectioned_symbol': detectioned_symbol}))
        logging.info("検出済銘柄の価格保存に成功しました")
    except Exception as e:
        logging.error(e)
    finally:
        file.close()

def get_detectioned_symbol_from_save_file(detection_price_rise_rate):
    logging.info("検出済銘柄の価格を外部ファイルから取得")
    detectioned_symbol = None
    file = None
    detection_price_rise_rate_formated = int(detection_price_rise_rate * 100)
    file_path = Const.DETECTIONED_SYMBOL_SAVE_FILE_PATH + "_" + str(detection_price_rise_rate_formated) + "_" + base_symbol + Const.FILE_TYPE_JSON

    try:
        file = open(file_path)
        detectioned_symbol_data = file.read()
        logging.info(detectioned_symbol_data)
        detectioned_symbol = json.loads(detectioned_symbol_data)["detectioned_symbol"]
    except Exception as e:
        logging.error(e)
    finally:
        if file != None:
            file.close()
    
    return detectioned_symbol

def add_detectioned_symbol(symbol, price_rise_rate):
    logging.info("検出済リストに追加")
    detectioned_symbol = get_detectioned_symbol_from_save_file(price_rise_rate)

    if detectioned_symbol == None or "list" not in detectioned_symbol.keys():
        detectioned_symbol = {"list":[], "losscut_count": 0}

    detectioned_symbol["list"].append(symbol)
    
    write_detectioned_symbol(detectioned_symbol, price_rise_rate)

def delete_detectioned_symbol(symbol_name, price_rise_rate):
    logging.info("検出済リストから削除")
    detectioned_symbol = get_detectioned_symbol_from_save_file(price_rise_rate)
    for index, detectioned_symbol_item in enumerate(detectioned_symbol["list"]):
        if detectioned_symbol_item["symbol"] == symbol_name:
            delete_target = detectioned_symbol["list"].pop(index)
            write_detectioned_symbol(detectioned_symbol, price_rise_rate)
            logging.info("検出済リストから削除しました:" + delete_target["symbol"])

def is_detectioned_symbol(symbol_name, price_rise_rate):
    result = False
    
    detectioned_symbol = get_detectioned_symbol_from_save_file(price_rise_rate)
    if detectioned_symbol == None:
        return False
    
    if "list" not in detectioned_symbol.keys() or len(detectioned_symbol["list"]) == 0:
        return False
    
    for detectioned_symbol_item in detectioned_symbol["list"]:
        if detectioned_symbol_item["symbol"] == symbol_name:
            logging.info("すでに検出済")
            result = True
    
    return result

def update_losscut_count(detection_price_rise_rate):
    detectioned_symbol = get_detectioned_symbol_from_save_file(detection_price_rise_rate)
    
    if detectioned_symbol == None:
        return
    
    detectioned_symbol["losscut_count"] = detectioned_symbol["losscut_count"] + 1 if "losscut_count" in detectioned_symbol.keys() else 1

    write_detectioned_symbol(detectioned_symbol, detection_price_rise_rate)

def get_blacklist_symbol_from_save_file():
    logging.info("ブラックリスト銘柄を外部ファイルから取得")
    blacklist_symbol = []
    file = None

    try:
        file = open(Const.BLACKLIST_SYMBOL_SAVE_FILE_PATH)
        blacklist_symbol_data = file.read()
        logging.info(blacklist_symbol_data)
        blacklist_symbol = json.loads(blacklist_symbol_data)["blacklist"]
    except Exception as e:
        logging.error(e)
    finally:
        if file != None:
            file.close()
    
    return blacklist_symbol

def is_blacklist_symbol(symbol_name):
    result = False
    
    blacklist_symbol = get_blacklist_symbol_from_save_file()
    
    if len(blacklist_symbol) == 0:
        return False
    
    for blacklist_symbol_item in blacklist_symbol:
        if blacklist_symbol_item == symbol_name:
            result = True
    
    return result

def notify_analyze_result(detection_price_rise_rate_list, price_rise_rate_list):
    for detection_price_rise_rate_item in detection_price_rise_rate_list:
        detectioned_symbol = get_detectioned_symbol_from_save_file(detection_price_rise_rate_item)
        
        if detectioned_symbol == None:
            logging.info("検出済銘柄を取得できませんでした")
            logging.info("レート: " + str(detection_price_rise_rate_item))
        else:
            aggregate_result = Aggregate().get_aggregate_result(detectioned_symbol, price_rise_rate_list)
            title = "bamboo集計 - 検出上昇値幅:" + str(detection_price_rise_rate_item)
            notify_bamboo(title, aggregate_result)

def get_chatwork_api_messages_url(room_id):
    return Const.CHATWORK_API_BASE_URL + Const.CHATWORK_ENDPOINT_ROOMS_PATH + '/' + str(room_id) + Const.CHATWORK_ENDPOINT_MESSAGES_PATH
    
def notify_bamboo(title, bamboo):
    
    headers = {
        "X-ChatWorkToken" : token
    }

    param = {
        'body': '[info][title]' + title + '[/title]' + json.dumps(bamboo) + '[/info]',
        'self_unread' : 1
    }
    data = urllib.parse.urlencode(param).encode('utf-8')
    send_message_api = get_chatwork_api_messages_url(my_room_id)
    send_message_req = urllib.request.Request(send_message_api, data, headers=headers)
    send_message_res = urllib.request.urlopen(send_message_req)
    
    result_message = ""
    if send_message_res.getcode()  == 200 :
        message_id = json.loads(send_message_res.read().decode('utf8'))
        print(message_id)
        result_message = 'Success Send Info!! message_id:' + str(message_id)
    else :
        result_message = 'Failed Send Info ...'
    logging.info(result_message)

now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d')
log_level = logging.DEBUG if Const.LOG_LEVEL == 0 else logging.INFO

logging.basicConfig(
    handlers=[RotatingFileHandler("bot" + today + ".log", maxBytes=1000000, backupCount=2)], level = log_level,
                       format='[%(asctime)s] %(module)s.%(funcName)s %(levelname)s -> %(message)s')

logging.info('start bot')
logging.info('Version:' + Const.VERSISON)

with open('settings.json') as settings:
    setting_data = json.loads(settings.read())
    access_key = setting_data['access_key']
    secret_key = setting_data['secret_key']
    price_check_interval = setting_data['price_check_interval']
    price_rise_rate_list = setting_data['price_rise_rate_list']
    losscut_price_rate = setting_data['losscut_price_rate']
    detection_price_rise_rate_list = setting_data['detection_price_rise_rate_list']
    base_symbol = setting_data["symbol"]
    token = setting_data['chatwork_api_token']
    my_room_id = setting_data['chatwork_room_id']
    is_notify = setting_data["notify"]
    
client = Client(access_key, secret_key)
last_save_time = None

while True:
    print('Version:' + Const.VERSISON)
    print("executing...")
    
    #全銘柄の価格を保存
    dt_now = datetime.datetime.now()
    if last_save_time == None:
        save_all_price(base_symbol)
        last_save_time = dt_now
    elif last_save_time.day != dt_now.day and dt_now.hour == "9":
        notify_analyze_result(detection_price_rise_rate_list, price_rise_rate_list)
        save_all_price(base_symbol)
        last_save_time = dt_now
    
    logging.info("価格保存日時:")
    logging.info(last_save_time)
        
    # 保持している全銘柄の価格を取得
    saved_all_price = get_all_price_from_save_file()
    
    # 価格が閾値以上上昇しているチェック
    res_all_price = None
    try:
        res_all_price = client.get_all_tickers()
    except Exception as  e:
        logging.error(e)
    
    if res_all_price != None:
        for res_all_price_item in res_all_price:
            
            if not is_blacklist_symbol(res_all_price_item["symbol"].replace(base_symbol, "")):
                is_not_saved_symbol = True
                for saved_all_price_item in saved_all_price:
                    if saved_all_price_item["symbol"] == res_all_price_item["symbol"]:
                        logging.info(saved_all_price_item["symbol"])
                        is_not_saved_symbol = False

                        # 上昇率を算出
                        rise_value = float(res_all_price_item["price"]) - float(saved_all_price_item["price"])
                        logging.info("-----------------------")
                        logging.info("rise_value:" + str(rise_value))
                        price_rise_rate = rise_value / float(saved_all_price_item["price"])
                        logging.info("rise_value / price:" + str(price_rise_rate))
                        logging.info("-----------------------")

                        # 検出した場合、上昇率に応じたファイルへ保存
                        for detection_price_rise_rate_item in detection_price_rise_rate_list:
                            logging.info("検出レート:" + str(detection_price_rise_rate_item))
                            if price_rise_rate >= detection_price_rise_rate_item and not is_detectioned_symbol(res_all_price_item["symbol"], detection_price_rise_rate_item):
                                logging.info("検出")
                                logging.info("上昇率: " + str(price_rise_rate))
                                logging.info("銘柄: " + res_all_price_item["symbol"])
                                res_all_price_item["detection_time"] = time.time()
                                add_detectioned_symbol(res_all_price_item, detection_price_rise_rate_item)
            
                if is_not_saved_symbol and base_symbol in res_all_price_item["symbol"] and check_ng_word(res_all_price_item["symbol"]):
                    # 新規価格チェック銘柄として追加
                    logging.info("価格チェック銘柄に追加")
                    logging.info("銘柄: " + res_all_price_item["symbol"])
                    add_all_price(res_all_price_item)
                
                # 検出済の場合、上昇率をチェック
                for detection_price_rise_rate in detection_price_rise_rate_list:
                    detection_symbol = None
                    detection_symbol_data = get_detectioned_symbol_from_save_file(detection_price_rise_rate)
                    detection_symbol_list = detection_symbol_data["list"] if detection_symbol_data != None and "list" in detection_symbol_data.keys() else []

                    for detection_symbol_item in detection_symbol_list:
                        if res_all_price_item["symbol"] == detection_symbol_item["symbol"]:
                            detection_symbol = detection_symbol_item

                    if detection_symbol != None:
                        detection_symbol_price = float(detection_symbol["price"])
                        rise_value = float(res_all_price_item["price"]) - detection_symbol_price
                        logging.info("-----------------------")
                        logging.info("rise_value:" + str(rise_value))
                        logging.info("detection_price_rise_rate:" + str(detection_price_rise_rate))
                        price_rise_rate = rise_value / detection_symbol_price
                        logging.info("rise_value / price:" + str(price_rise_rate))
                        logging.info("-----------------------")

                        is_losscut = -losscut_price_rate >= price_rise_rate
                        if is_losscut:
                            # 検出済銘柄から削除し、損切りカウントを増加
                            logging.info("--損切り--")
                            logging.info(detection_symbol["symbol"])
                            delete_detectioned_symbol(detection_symbol["symbol"], detection_price_rise_rate)
                            update_losscut_count(detection_price_rise_rate)

                        else:
                            for price_rise_rate_item in price_rise_rate_list:
                                if price_rise_rate >= price_rise_rate_item:
                                    if "price_rise_rate_list" not in detection_symbol.keys() or len(detection_symbol["price_rise_rate_list"]) == 0:
                                        # 検出済銘柄の上昇率リストに追加
                                        detection_time = time.time()
                                        detection_symbol["price_rise_rate_list"] = []
                                        detection_symbol["price_rise_rate_list"].append({"price_rise_rate": price_rise_rate_item, "time": detection_time})
                                        delete_detectioned_symbol(detection_symbol["symbol"], detection_price_rise_rate)
                                        add_detectioned_symbol(detection_symbol, detection_price_rise_rate)

                                    else:
                                        is_exist_price_rate = False
                                        for detection_price_rise_rate_item in detection_symbol["price_rise_rate_list"]:
                                            if detection_price_rise_rate_item["price_rise_rate"] == price_rise_rate_item:
                                                # すでにデータにある
                                                logging.info("上昇率データあり")
                                                is_exist_price_rate = True
                                        
                                        if not is_exist_price_rate:
                                            # 検出済銘柄の上昇率リストに追加
                                            detection_time = time.time()
                                            detection_symbol["price_rise_rate_list"].append({"price_rise_rate": price_rise_rate_item, "time": detection_time})
                                            delete_detectioned_symbol(detection_symbol["symbol"], detection_price_rise_rate)
                                            add_detectioned_symbol(detection_symbol, detection_price_rise_rate)
                                            
    time.sleep(price_check_interval)