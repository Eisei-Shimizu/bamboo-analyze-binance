class Const:
    VERSISON = "bamboo-analyze-v1"
    ALL_PRICE_SAVE_FILE_PATH = "./all_price.json"
    ALL_PRICE_SAVE_INTERVAL = 24 * 60 * 60 #24h
    DETECTIONED_SYMBOL_SAVE_FILE_PATH = "./detectioned/detectioned"
    AGGREGATE_SAVE_FILE_PATH = "./aggregate/aggregate"
    BLACKLIST_SYMBOL_SAVE_FILE_PATH = "./blacklist.json"
    FILE_TYPE_JSON = ".json"
    LOG_LEVEL = 0 # 0:debug 1:info
    CHATWORK_API_BASE_URL = 'https://api.chatwork.com/v2/'
    CHATWORK_ENDPOINT_ME_PATH = '/me'
    CHATWORK_ENDPOINT_ROOMS_PATH = '/rooms'
    CHATWORK_ENDPOINT_MESSAGES_PATH = '/messages'