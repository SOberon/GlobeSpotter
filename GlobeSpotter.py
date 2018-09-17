import unittest

class main:

    def main(self):
        pass

    def file_reader(self):
        import re

        file = open("temp.log")
        ipList = []

        for line in file:
            ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
            ipList.append(ip)


class UnitTests(unittest.TestCase):

    def empty_test(self):
        pass

    if __name__ == "__main__": main()
