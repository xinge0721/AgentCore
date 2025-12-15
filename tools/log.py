import os
import datetime

class Logger:
    """
    日志记录器，日志默认存储到record目录下，
    按日期分类（YYYY-MM-DD.log），自动尾插，
    记录时间和问题描述。
    """

    LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }

    def __init__(self, level='INFO', enable_console=True, record_dir='../Data/record'):
        """
        初始化 Logger

        Args:
            level (str): 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
            enable_console (bool): 是否打印到控制台
            record_dir (str): 日志文件目录（相对于log.py所在目录）
        """
        self.level = self.LEVELS.get(level.upper(), 20)
        self.enable_console = enable_console
        
        # 如果是相对路径，则相对于当前文件所在目录
        if not os.path.isabs(record_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.record_dir = os.path.join(current_dir, record_dir)
        else:
            self.record_dir = record_dir

        # 创建日志目录
        if not os.path.exists(self.record_dir):
            os.makedirs(self.record_dir)

    def _get_log_file(self):
        """获取当天日志文件路径"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.record_dir, f"{today}.log")

    def _log(self, level_str, msg):
        """
        内部方法，处理实际日志输出
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{now}] [{level_str}] {msg}"
        # 输出到控制台
        if self.enable_console and self.LEVELS[level_str] >= self.level:
            print(log_line)
        # 输出到文件（尾插写入）
        if self.LEVELS[level_str] >= self.level:
            log_file = self._get_log_file()
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(log_line + "\n")
            except Exception as e:
                if self.enable_console:
                    print(f"[Logger] 写入日志文件失败: {e}")

    def clear_log(self):
        """清空当天日志文件记录"""
        log_file = self._get_log_file()
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("")
            
    def debug(self, msg):
        self._log('DEBUG', msg)

    def info(self, msg):
        self._log('INFO', msg)

    def warning(self, msg):
        self._log('WARNING', msg)

    def error(self, msg):
        self._log('ERROR', msg)

    def critical(self, msg):
        self._log('CRITICAL', msg)

# 使用示例
# logger = Logger(level="DEBUG", enable_console=True)
# logger.info("程序启动")
# logger.error("发生错误: xxxx")

# 全局日志记录器
logger = Logger(level="DEBUG", enable_console=True)