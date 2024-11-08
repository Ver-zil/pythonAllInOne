import patoolib.util


def extract_archive(archive_path, dest_dir, password):
    """
    解压带有密码的压缩文件。

    :param archive_path: 压缩文件的路径。
    :param dest_dir: 解压目标目录。
    :param password: 解压密码。
    """
    # 调用 patoolib 来解压
    patoolib.util.extract(archive_path, outdir=dest_dir, pwd=password)
    print(f"解压完成: {archive_path} -> {dest_dir}")


# 压缩文件路径
archive_path = r'D:\BaiduNetdiskDownload\sundasheng\20240826 东大到底有没有无锚印钞？未来会通货膨胀吗？\20240826 东大到底有没有无锚印钞？未来会通货膨胀吗？（图文版本.zip'
# 解压密码
password = 'sundasheng'
# 解压后的目录
dest_dir = 'path/to/destination/directory'

# 调用函数进行解压
extract_archive(archive_path, dest_dir, password)
