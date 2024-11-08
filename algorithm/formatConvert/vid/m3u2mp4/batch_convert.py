from algorithm.formatConvert.vid.m3u2mp4.m3u2mp4 import convert_to_mp4

# 调用：
film_name = ''
file = r'E:\\1\\file\\' + film_name + '.m3u8'
save_path = r'E:\\1\\file\\' + film_name + '.mp4'
convert_to_mp4(file, save_path)
