from abc import ABCMeta, abstractmethod


class Logger:
    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self, data):
        pass

    @abstractmethod
    def close(self):
        pass


class FileWriterLogger(Logger):

    def __init__(self, file_name: str):
        self.file = open(file_name, 'a')

    def write(self, data):
        self.file.write(data)

    def close(self):
        self.file.close()


class DisabledLogger(Logger):

    def write(self, data):
        pass

    def close(self):
        pass
