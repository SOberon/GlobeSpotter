import unittest
import re
import socket
import tokenize
import pydoc


class main:

    def main(self):
        pass

    def valid_ip(input_file):
        """
        https://stackoverflow.com/questions/11264005/using-a-regex-to-match-ip-addresses-in-python/11264056

        Parse a .txt file for IPv4 and IPv6 addresses.

        Args:
            input_file: A .txt file to be parsed.

        :return: A list of IP addresses.
        """

        ip_list = []

        tokens = tokenize.open(input_file)

        for ip in tokens:

            if socket.inet_aton(ip):
                ip_list.append(ip)

        return ip_list


    # def get_ipv6s_from_file(input_file):
    #     """
    #     https://stackoverflow.com/questions/14026529/python-parse-file-for-ip-addresses
    #
    #     Parse a .txt file for IPv4 and IPv6 addresses.
    #
    #     Args:
    #         input_file: A .txt file to be parsed.
    #
    #     :return: A list of IP addresses.
    #     """
    #
    #     ip_list = []
    #
    #     ip_list.extend(CleanData(input_file).to_list())
    #
    #     return ExtractIPs(ip_list).get_ipv4_results()

class UnitTests(unittest.TestCase):

    def empty_test(self):
        pass

    if __name__ == "__main__": main()
