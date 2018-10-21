import unittest
import ipaddress
import csv
import sys
from geolite2 import geolite2
from ipwhois import IPWhois

# class GlobeSpotter:
# To run in terminal, python GlobeSpotter.py <filename>
# file_name = sys.argv[1]
file_name = "file.csv"


def __init__(self, file):
    self.file_name = file


def main(self):
    display_title()
    valid_addresses = self.add_valid_addresses_to_list(self.file_name)
    geoip_data = get_geoip_data(valid_addresses)
    rdap_data = get_rdap_data(valid_addresses)
    display_geoip_and_rdap_data(geoip_data, rdap_data)


# ASCII art tomfoolery
def display_title():
    print("  _____ _       _           _____             _   _\n" +
          "/ ____| |      | |         / ____|           | | | |\n" +
          "| |  __| | ___ | |__   ___| (___  _ __   ___ | |_| |_ ___ _ __\n" +
          "| | |_ | |/ _ \| '_ \ / _ " + r"\\" + "___ \| '_ \ / _ \| __| __/ _ \ '__|\n" +
          "| |__| | | (_) | |_) |  __/____) | |_) | (_) | |_| ||  __/ |\n" +
          " \_____|_|\___/|_.__/ \___|_____/| .__/ \___/ \__|\__\___|_|\n" +
          "                                 | |\n" +
          "                                 |_|")


# Checks if an IP address is valid by querying the ipaddress module. Bad IPs return a ValueError from ipaddress.
def check_if_valid_address(ip):
    try:
        potential_address = ipaddress.ip_address(ip)
        return str(potential_address)

    except ValueError:
        return

    except TypeError:
        return


# Parses a .csv file for valid IP addresses and returns them as a list. Ignores any non-valid addresses.
def add_valid_addresses_to_list(input_file):
    ip_list = []

    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            for token in row:
                if check_if_valid_address(token) is not None:
                    ip_list.append(token)

    return ip_list


# Iterates through a list of valid IP addresses and returns GeoIP location data as a dictionary value.
def get_geoip_data(ip_list):
    geoip_data = {}
    reader = geolite2.reader()

    # If ip_list is empty, stop doing work
    if not ip_list:
        geoip_data.update({"No valid IP addresses.":
                               ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]})
        return geoip_data

    for ip in ip_list:
        data_list = []

        try:
            match = reader.get(ip)

            if match is None:
                geoip_data.update({"No data available in geolite2.":
                                    ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]})

                return geoip_data

            # City                  -> {'city': {'names': {'en': value}}
            data_list.append(match.get('city', {}).get('names', {}).get('en'))

            # Accuracy radius       -> {'location': {'longitude': value}}
            data_list.append(match.get('location', {}).get('accuracy_radius'))

            # Latitude              -> {'location': {'latitude': value}}
            data_list.append(match.get('location', {}).get('latitude'))

            # Longitude             -> {'location': {'longitude': value}}
            data_list.append(match.get('location', {}).get('longitude'))

            # Postal code           -> {'location': {'postal': value}}
            data_list.append(match.get('location', {}).get('postal'))

            # Metro code            -> {'location': {'metro_code': value}}
            data_list.append(match.get('location', {}).get('metro_code'))

            # State or subdivision  -> {'subdivisions': [{'names': {'en': value}}]} {key: list[key2: {key: value}]}
            data_list.append(match.get('subdivisions')[0].get('names', {}).get('en'))

            # Time zone             -> {'location': {'time_zone': value}}
            data_list.append(match.get('location', {}).get('time_zone'))

            # Country               -> {'country': {'names': {'en': value}}
            data_list.append(match.get('country', {}).get('names', {}).get('en'))

            # Continent             -> {'continent': {'names': {'en': }}
            data_list.append(match.get('continent', {}).get('names', {}).get('en'))

            geoip_data.update({ip: data_list})

        except ValueError:
            geoip_data.update({"No GeoIP/location data available for this IP.":
                                   ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]})

    geolite2.close()
    return geoip_data


def get_rdap_data(ip_list):
    rdap_data = {}

    # If ip_list is empty, stop doing work
    if not ip_list:
        rdap_data.update({"No valid IP addresses.":
                               ["None", "None", "None", "None", "None", "None"]})
        return rdap_data

    for ip in ip_list:
        data_list = []
        obj = IPWhois(ip)
        results = obj.lookup_rdap(depth=1)

        data_list.append(results.get('asn'))
        data_list.append(results.get('asn_cidr'))
        data_list.append(results.get('asn_country_code'))
        data_list.append(results.get('asn_date'))
        data_list.append(results.get('asn_description'))
        data_list.append(results.get('asn_registry'))

        rdap_data.update({ip: data_list})

    return rdap_data

def display_geoip_and_rdap_data(geoip, rdap):
    pass

# TODO figure out a way to get print statements to work with unit tests. Super low priority.
# class TestDisplayTitle(unittest.TestCase):
#     def test_title(self):
#         self.assertEqual("  _____ _       _           _____             _   _\n" +
#                          "/ ____| |      | |         / ____|           | | | |\n" +
#                          "| |  __| | ___ | |__   ___| (___  _ __   ___ | |_| |_ ___ _ __\n" +
#                          "| | |_ | |/ _ \| '_ \ / _ " + r"\\" + "___ \| '_ \ / _ \| __| __/ _ \ '__|\n" +
#                          "| |__| | | (_) | |_) |  __/____) | |_) | (_) | |_| ||  __/ |\n" +
#                          " \_____|_|\___/|_.__/ \___|_____/| .__/ \___/ \__|\__\___|_|\n" +
#                          "                                 | |\n" +
#                          "                                 |_|", display_title())


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


class TestGetGeoipData(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual({"No valid IP addresses.":
                              ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         get_geoip_data([]))

    def test_list_is_all_junk(self):
        self.assertEqual({"No GeoIP/location data available for this IP.":
                              ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         get_geoip_data(["Foobar"]))

    # def test_list_has_one_IPv4_geolite2_match_with_no_available_data(self):
    #     self.assertEqual({"No data available.":
    #                                 ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
    #                      get_geoip_data(["17.0.0.0"]))

    def test_list_has_one_good_IPv4_geolite2_match(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America']},
                         get_geoip_data(["17.0.0.1"]))

    def test_list_has_one_IPv6_geolite2_match_with_no_available_data(self):
        self.assertEqual({"No data available in geolite2.":
                                    ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         get_geoip_data(["2001:db:8::"]))

    # TODO IPv6 addresses aren't returning geolite2 results. Problem with my code, the database, or the IP addresses?
    # def test_list_has_one_good_IPv6_geolite2_match(self):
    #     self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
    #                                    'America/Los_Angeles', 'United States', 'North America']},
    #                      get_geoip_data(["2001:4860:0:2001::68"]))

    def test_list_has_one_good_IPv4_geolite2_matche_and_some_junk(self):
        self.assertEqual({"No GeoIP/location data available for this IP.":
                            ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"],
                          "17.0.0.1":
                            ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California', 'America/Los_Angeles',
                             'United States', 'North America'],
                          "No GeoIP/location data available for this IP.":
                            ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         get_geoip_data(["Foobar", "17.0.0.1", "Barfoo"]))

    def test_list_has_two_good_IPv4_geolite2_matches(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America'],
                          "73.78.160.191": ['Aurora', 5, 39.6603, -104.7681, None, 751, 'Colorado',
                                            'America/Denver', 'United States', 'North America']},
                         get_geoip_data(["17.0.0.1", "73.78.160.191"]))

    # def test_list_has_two_good_IPv6_geolite2_matches(self):
    #     self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
    #                                    'America/Los_Angeles', 'United States', 'North America']},
    #                      get_geoip_data(["17.0.0.1"]))

    # def test_list_has_one_good_IPv4_and_one_good_IPv6_geolite2_match(self):
    #     self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
    #                                    'America/Los_Angeles', 'United States', 'North America']},
    #                      get_geoip_data(["17.0.0.1"]))


class TestGetRdapData(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual({"No valid IP addresses.":
                            ["None", "None", "None", "None", "None", "None"]},
                         get_rdap_data([]))

    def test_list_has_one_good_IPv4_whois_match(self):
        self.assertEqual({"74.125.225.229":
                            ['15169', '74.125.225.0/24', 'US', '2007-03-13', 'GOOGLE - Google LLC, US', 'arin']},
                         get_rdap_data(['74.125.225.229']))

    def test_list_has_two_good_IPv4_whois_matches(self):
        self.assertEqual({"74.125.225.229":
                            ['15169', '74.125.225.0/24', 'US', '2007-03-13', 'GOOGLE - Google LLC, US', 'arin'],
                          "17.0.0.1":
                              ['714', '17.0.0.0/21', 'US', '1990-04-16', 'APPLE-ENGINEERING - Apple Inc., US', 'arin']
                          },
                         get_rdap_data(['74.125.225.229', '17.0.0.1']))

    def test_list_has_one_good_IPv6_whois_match(self):
        self.assertEqual({"2001:4860:0:2001::68":
                            ['15169', '2001:4860::/32', 'US', '2005-03-14', 'GOOGLE - Google LLC, US', 'arin']},
                         get_rdap_data(['2001:4860:0:2001::68']))


if __name__ == '__main__':
    unittest.main()
