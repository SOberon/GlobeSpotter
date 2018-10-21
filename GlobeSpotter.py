import unittest
import ipaddress
import csv
import sys
from geoip import geolite2  # https://pythonhosted.org/python-geoip/

# class GlobeSpotter:
# To run in terminal, python GlobeSpotter.py <filename>
# fileName = sys.argv[1]
fileName = "file.csv"

def __init__(self, file_name):
    self.file_name = file_name

def main(self):
    valid_addresses = self.add_valid_addresses_to_list(self.file_name)
    # geoip_data = get_geoip_Data(valid_addresses)
    # rdap_data = get_rdap_data(valid_addresses)


def check_if_valid_address(ip):
    try:
        potential_address = ipaddress.ip_address(ip)
        return str(potential_address)

    except ValueError:
        return

    except TypeError:
        return


def add_valid_addresses_to_list(input_file):
    ip_list = []

    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            for token in row:
                if check_if_valid_address(token) is not None:
                    ip_list.append(token)

    return ip_list


def get_location_data(ip_list):
    geoip_and_rdap_data = {}

    for ip in ip_list:
        data_list = []

        match = geolite2.lookup(ip)

        if match is None:
            data_list.append("No GeoIP data available")

        else:
            data_list.append(match.country)
            data_list.append(match.continent)
            data_list.append(match.location)
            data_list.append(match.timezone)
            data_list.append(match.subdivisions)

        # Append the following to data_list:
        #     Registration country (maybe)
        #     ISP name, address, abuse email (?)
        #     If registered, the domain name
        #     Registration and expiry dates

        geoip_and_rdap_data.update({ip, data_list})


class TestCheckIfValidAddress(unittest.TestCase):
    def test_IPv4_address_is_valid(self):
        self.assertEqual("192.168.0.1", check_if_valid_address('192.168.0.1'))

    def test_IPv6_address_is_valid(self):
        self.assertEqual("2001:db:8::", check_if_valid_address('2001:db:8::'))

    def test_IP_address_is_not_valid(self):
        self.assertEqual(None, check_if_valid_address("Foobar"))


class TestAddValidAddressesToList(unittest.TestCase):
    def test_empty_file(self):
        self.assertEqual([], add_valid_addresses_to_list("empty_file.csv"))

    def test_file_with_no_valid_entries(self):
        self.assertEqual([], add_valid_addresses_to_list("no_valid_entries.csv"))

    def test_file_with_one_valid_entry(self):
        self.assertEqual(["192.168.0.1"], add_valid_addresses_to_list("one_valid_entry.csv"))

    def test_file_with_one_valid_entry_and_some_junk(self):
        self.assertEqual(["192.168.0.1"], add_valid_addresses_to_list("one_valid_entry_and_some_junk.csv"))

    def test_file_with_one_row_of_valid_entry_and_some_junk(self):
        self.assertEqual(["192.168.0.1"], add_valid_addresses_to_list("one_row_of_valid_entry_and_some_junk.csv"))

    def test_file_with_two_rows_of_valid_entries(self):
        self.assertEqual(['192.168.0.1', '2001:db:8::', '2001:db:8::', '192.168.0.1'],
                         add_valid_addresses_to_list("two_rows_of_valid_entries.csv"))

    def test_file_with_two_rows_of_valid_entries_and_some_junk(self):
        self.assertEqual(["192.168.0.1", "192.168.0.1", "2001:db:8::"],
                         add_valid_addresses_to_list("two_rows_of_valid_entries_and_some_junk.csv"))

    def test_file_with_several_rows_of_valid_entries_and_some_junk(self):
        self.assertEqual(["192.168.0.1", "192.168.0.1", "192.168.0.1", "2001:db:8::", "192.168.0.1", "2001:db:8::",
                          "192.168.0.1", "192.168.0.1", "192.168.0.1", "2001:db:8::", "192.168.0.1", "2001:db:8::",
                          "192.168.0.1", "192.168.0.1", "192.168.0.1", "2001:db:8::", "192.168.0.1", "2001:db:8::"],
                         add_valid_addresses_to_list("several_rows_of_valid_entries_and_some_junk.csv"))


class TestGetLocationData(unittest.TestCase):
    def test_empty_list(self):
        pass

    def test_list_is_all_junk(self):
        pass

    def test_list_has_one_good_geolite2_match(self):
        pass

    def test_list_has_one_good_geolite2_match_and_some_junk(self):
        pass

    def test_list_has_two_good_geolite2_matches(self):
        pass

    def test_list_has_two_good_geolite2_matches_and_some_junk(self):
        pass

if __name__ == '__main__':
    unittest.main()
