def dict_integration(dict_data_list):
    all_data = []
    all_keys = set()
    for item in dict_data_list:
        all_keys.update(item.keys())
    for idx, item in enumerate(dict_data_list):
        # 为缺失的键添加None值
        all_data.append({key: item.get(key, None) for key in all_keys})

    return all_data
