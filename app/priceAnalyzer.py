from datetime import datetime, timedelta


class Analyzer:
    def get_start_time(self):
        now = datetime.now() - timedelta(days=6)
        now = datetime.strftime(now, "%d/%m/%Y %H:%M:%S")
        return now
    

    def get_new_wanted_price(self,i_id):
        start_time = self.get_start_time()
           
        price_list = self.db.get_daily_prices(i_id, start_time)


        ph_list = []
        def get_pre_high(nums, ph_list):
            
            if len(nums)<=2:
                return 0
            m = max(nums)
            l = nums[:nums.index(m)]
            r = nums[nums.index(m)+1:]
            
            if len(l)<1:
                return get_pre_high(r, ph_list)

            ph_list.append(max(l))
        
            get_pre_high(r, ph_list)

            return max(ph_list)

        max_recorded_price = get_pre_high(price_list, ph_list)

        descreased_max_price = max_recorded_price * 0.975
        sell_with_fee = descreased_max_price * 0.85
        wanted_price =round(sell_with_fee * 0.9 ,2 )

        return wanted_price

    def update_items_info_wanted_price(self, item_id):
        wanted_price = self.get_new_wanted_price(item_id)
        self.db.update_wanted_price(item_id, wanted_price)
        return wanted_price
        
            

        
