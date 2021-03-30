import time

class Aggregate:
    
    def get_aggregate_result(self, detectioned_symbol, price_rise_rate_list):
        w1_list = {}
        w2_list = {}
        m1_list = {}
        losscut_count = None
        day = 3600 * 24
        w1 = day * 7
        w2 = day * 14
        m1 = w2 * 2
        now = time.time()
        
        #期間別集計リストを初期化
        for price_rise_rate_item in price_rise_rate_list:
            w1_list.update({str(price_rise_rate_item): 0})
            w2_list.update({str(price_rise_rate_item): 0})
            m1_list.update({str(price_rise_rate_item): 0})
            
        if "list" in detectioned_symbol.keys():
            for detectioned_symbol_item in detectioned_symbol["list"]:
                # 期間べつに集計
                if "price_rise_rate_list" in detectioned_symbol_item.keys():
                    for symbol_price_rise_rate_item in detectioned_symbol_item["price_rise_rate_list"]:
                        index = str(symbol_price_rise_rate_item["price_rise_rate"])
                        if detectioned_symbol_item["detection_time"] + w1 >= symbol_price_rise_rate_item["time"]:
                            w1_list[index] = w1_list[index] + 1
                        
                        if detectioned_symbol_item["detection_time"] + w2 >= symbol_price_rise_rate_item["time"]:
                            w2_list[index] = w2_list[index] + 1
                        
                        if detectioned_symbol_item["detection_time"] + m1 >= symbol_price_rise_rate_item["time"]:
                            m1_list[index] = m1_list[index] + 1
            
        
        if "losscut_count" in detectioned_symbol.keys():
            losscut_count = detectioned_symbol["losscut_count"]
           
        result = {"w1": w1_list, "w2": w2_list, "m1": m1_list, "losscut_count": losscut_count}
        
        return result