import logging


def set_loggers():
    # 设置日志级别为DEBUG，并设置输出格式
    logging.basicConfig(level=logging.WARN,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='crawler.log',
                        filemode='w')

    # 创建一个stream handler，用于输出到控制台
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console_logger.setFormatter(formatter)
    logging.getLogger('').addHandler(console_logger)
