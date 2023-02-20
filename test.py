from app.DB import BaseDB

g = "WHERE dt BETWEEN '11/02/2023 00:00:00' and '20/02/2023 20:56:01'"
db = BaseDB()
db.connect()
data = db.cur.execute("""SELECT qty, price, dt from item946""").fetchall()
print(data)

from collections import defaultdict

a = defaultdict(int)

for i in range(len(data)-1):
    if data[i][1] < data[i+1][1] and (data[i][0] - data[i+1][0])>0:
        a[data[i][1]]+=(data[i][0] - data[i+1][0])

for key, value in sorted(a.items()):
    print(key, value)


# nums = [6.9, 6.8, 6.7, 6.9, 6.8, 7, 6,5]
# ph_list = []
# def get_pre_high(nums, ph_list):
    
#     if len(nums)<=2:
#         return 0
#     m = max(nums)
#     l = nums[:nums.index(m)]
#     r = nums[nums.index(m)+1:]
    
#     if len(l)<1:
#         return get_pre_high(r, ph_list)

#     ph_list.append(max(l))
  
#     get_pre_high(r, ph_list)

#     return max(ph_list)
    

# print(get_pre_high(nums, ph_list))


# from app.DB import BaseDB

# a = BaseDB()
# a.connect()

# a.DELETE()
