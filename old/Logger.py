import logging


class Logger:
    def __init__(self, name='stock', level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 创建一个控制台Handler，并设置日志级别
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        # 创建一个Formatter对象，并设置格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 创建一个文件Handler，并设置日志级别
        # file_handler = logging.FileHandler('log_file.log')
        # file_handler.setLevel(level)
        # file_handler.setFormatter(formatter)
        # 将console_handler/fileHandler对象添加到logger对象中
        # self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

log = Logger().get_logger()

if __name__ == '__main__':
    # 输出日志信息
    log.debug('This is a debug message.')
    log.info('This is an info message.')
    log.warning('This is a warning message.')
    log.error('This is an error message.')
    log.critical('This is a critical message.')
