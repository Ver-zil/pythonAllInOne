import subprocess


def convert_to_mp4(input_file, output_file):
    command = ['ffmpeg', '-i', input_file, '-c', 'copy', output_file]

    try:
        # 运行命令并等待其结果
        result = subprocess.run(command, check=True)

        if result.returncode == 0:
            print("转换成功！")

    except FileNotFoundError:
        print("未安装FFmpeg或者路径设置不正确。请先安装FFmpeg并添加到系统的PATH中。")


