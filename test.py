nums = [6.9, 6.8, 6.7, 6.9, 6.8, 7, 6,5]



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
    

print(get_pre_high(nums, ph_list))

