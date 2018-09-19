import unittest
import pydoc
import IPaddresses
import Data

from Data import CleanData  # Format and clean the data
from IPAddresses import ExtractIPs



class main:

    def main(self):
        pass

    def get_ipv4s_from_file(input_file):
        """
        https://stackoverflow.com/questions/14026529/python-parse-file-for-ip-addresses

        Parse a .txt file for IPv4 and IPv6 addresses.

        Args:
            input_file: A .txt file to be parsed.

        :return: A list of IP addresses.
        """

        ip_list = []

        ip_list.extend(CleanData(input_file).to_list())

        return ExtractIPs(ip_list).get_ipv4_results()

    def get_ipv6s_from_file(input_file):
        """
        https://stackoverflow.com/questions/14026529/python-parse-file-for-ip-addresses

        Parse a .txt file for IPv4 and IPv6 addresses.

        Args:
            input_file: A .txt file to be parsed.

        :return: A list of IP addresses.
        """

        ip_list = []

        ip_list.extend(CleanData(input_file).to_list())

        return ExtractIPs(ip_list).get_ipv4_results()

class UnitTests(unittest.TestCase):

    def empty_test(self):
        pass

    if __name__ == "__main__": main()
