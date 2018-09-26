import unittest
import socket
import tokenize
import pydoc

from geoip import geolite2

class GlobeSpotter:

    def main(self):
        pass

    def get_file(self):
        return input("Please enter name of file.")

    def valid_ip(self, input_file):
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

    def get_location_data(self, ip_list):
        geoip_and_ip_data = {}

        for ip in ip_list:
            data_list = []

            match = geolite2.lookup(ip)

            if match is None:
                data_list.append("No GeoIP data available")

            data_list.append(match.country)
            data_list.append(match.continent)
            data_list.append(match.location)
            data_list.append(match.timezone)
            data_list.append(match.subdivisions)


            data_list.append(rdap_lookup(ip))
            geoip_and_ip_data.update({ip, data_list})

    valid_ip(get_file)



class UnitTests(unittest.TestCase):

    def empty_test(self):
        pass

    if __name__ == "__main__": main()
