import unittest
import pydoc
# from unittest.mock import patch # Remove; patch is usually for API calls


class main:

    def main(self):
        pass

    def file_reader(self):
        """
        Reads a file, fill in more stuff later when you understand more of pydocs
        :return:
        """
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
