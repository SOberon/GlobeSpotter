import unittest
import ipaddress
import csv
import sys
from geolite2 import geolite2           # pip install maxminddb-geolite2
from ipwhois import IPWhois
import warnings
from tabulate import tabulate           # pip install tabulate

# Good list of sample IPs for testing https://tools.tracemyip.org/search--ip/list

# Before running, terminal <.\venv\Scripts\activate.bat>

# class GlobeSpotter:
# To run in terminal, python GlobeSpotter.py <filename>

# The following two lines disable warnings by default. To re-enable, run program with -w.
if not sys.warnoptions:
    warnings.simplefilter("ignore")

    # Uncomment for testing
    # file_name = "empty_file.csv"
    # file_name = "one_valid_entry.csv"
    # file_name = "two_rows_of_valid_entries.csv"
    # file_name = "test_file.csv"


# def __init__(self, file):
#     self.file_name = file


def main():
    print(display_title())

    file_name = prompt_for_file()

    valid_addresses = add_valid_addresses_to_list(file_name)

    geoip_data = get_geoip_data(valid_addresses)
    # print(geoip_data)

    rdap_data = get_rdap_data(valid_addresses)
    # print(rdap_data)

    print(display_geoip_and_rdap_data(geoip_data, rdap_data))


def prompt_for_file():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]

    else:
        print("Tip of the day: a file name may be passed in as an argument when opening the program." +
              " Example: python GlobeSpotter.py file.csv\n")
        file_name = input("Please enter the name of a .csv file to be read: ")

    return file_name


# ASCII art tomfoolery
def display_title():
    welcome = ("\n\n********************************************************************************\n" +
               " ****************************************************************************** \n" +
               "  _____ _       _           _____             _   _" + "                 .-'';'-.\n"
               " / ____| |     | |         / ____|           | | | |" + "              ,'   <_,-.`.\n"
               "| |  __| | ___ | |__   ___| (___  _ __   ___ | |_| |_ ___ _ __" + "   /)   ,--,_>\_\\\n"
               "| | |_ | |/ _ \| '_ \ / _ " + r"\\" + "___ \| '_ \ / _ \| __| __/ _ \ '__|" + " |'   (       \_|\n"
               "| |__| | | (_) | |_) |  __/____) | |_) | (_) | |_| ||  __/ |" + "    |_    `-.    / |\n"
               " \_____|_|\___/|_.__/ \___|_____/| .__/ \___/ \__|\__\___|_|" + "     \`-.   ;  _(`/\n"
               "                                 | |" + "                              `.(    \/ ,'\n"
               "                                 |_|" + "                                `-....-'\n" +
               " ****************************************************************************** \n" +
               "********************************************************************************\n\n")

    return welcome


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
    good = 0
    bad = 0

    print("Reading file...", end="", flush=True)

    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            for token in row:
                if check_if_valid_address(token) is not None:
                    ip_list.append(token)
                    good += 1
                else:
                    bad += 1

    print("Done.\n" +
          "********************\n\n")

    count_valid_addresses(good, bad)

    return ip_list


# Iterates through a list of valid IP addresses and returns GeoIP location data as a dictionary value.
def get_geoip_data(ip_list):
    geoip_data = {}
    reader = geolite2.reader()

    has_data = 0
    no_data = 0

    print("Looking up GeoIP (location) data...", end="", flush=True)

    # If ip_list is empty, stop doing work
    if not ip_list:
        count_valid_results("geolocation", has_data, no_data)

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

                no_data += 1
                break
                # return geoip_data

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
            if match.get('subdivisions'):
                data_list.append(match.get('subdivisions')[0].get('names', {}).get('en'))
            else:
                data_list.append(None)

            # Time zone             -> {'location': {'time_zone': value}}
            data_list.append(match.get('location', {}).get('time_zone'))

            # Country               -> {'country': {'names': {'en': value}}
            data_list.append(match.get('country', {}).get('names', {}).get('en'))

            # Continent             -> {'continent': {'names': {'en': }}
            data_list.append(match.get('continent', {}).get('names', {}).get('en'))

            geoip_data.update({ip: data_list})

            has_data += 1
            print('.', end="", flush=True)

        except ValueError:
            geoip_data.update({"No GeoIP/location data available for this IP.":
                                   ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]})

    count_valid_results("geolocation", has_data, no_data)

    geolite2.close()
    return geoip_data


def get_rdap_data(ip_list):
    rdap_data = {}
    has_data = 0
    no_data = 0

    print("Looking up RDAP (internet service provider) data.\n" +
          "Depending on the size of the file, this may take some time...", end="", flush=True)

    # If ip_list is empty, stop doing work
    if not ip_list:
        count_valid_results("ISP", has_data, no_data)

        rdap_data.update({"No valid IP addresses.": ["None", "None", "None", "None", "None", "None"]})

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

        has_data += 1
        print('.', end="", flush=True)

    count_valid_results("ISP", has_data, no_data)

    return rdap_data


# TODO put edge cases as separate methods; I don't like the clutter of this method.
def display_geoip_and_rdap_data(geoip, rdap):
    # geoip_header = ["IP Address", "City", "Radius", "Latitude", "Longitude", "Postal Code", "Metro Code",
    #                 "State/Region", "Time Zone", "Country", "Continent"]
    #
    # rdap_header = ["IP Address", "ASN", "ASN CIDR", "ASN Country Code", "ASN Date", "ASN Description", "ASN Registry"]
    #
    # no_geoip = "No valid GeoIP data was passed in."
    # no_rdap = "No valid RDAP data was passed in."
    #
    # # If GeoIP and RDAP dicts are empty
    # if not geoip and not rdap:
    #     print(no_geoip + "\n" + no_rdap)
    #
    # # If RDAP dict is empty
    # if not rdap:
    #     print(tabulate(geoip, headers=geoip_header))
    #     print("\n" + no_rdap)
    #
    # # If GeoIP dict is empty
    # if not geoip:
    #     print("\n" + no_geoip)
    #     print(tabulate(rdap, headers=rdap_header))
    #
    # # If GeoIP and RDAP dicts are not empty; that is, not an edge case
    # print(tabulate(geoip, headers=geoip_header) + "\n")
    # print(tabulate(rdap, headers=rdap_header))
    #
    # # full_output = tabulate(geoip, headers=geoip_header) + "\n" + tabulate(rdap, headers=rdap_header)
    #
    # return

    output = ""
    no_geoip = "No valid GeoIP data was passed in."
    no_rdap = "No valid RDAP data was passed in."

    sp = '{:>10}'.format('')  # GeoIP spacing
    rp = '{:>10}'.format('')  # RDAP spacing

    geoip_header = ("IP Address" + sp + "City" + sp + "Radius" + sp + "Latitude" + sp + "Longitude" + sp + "Postal Code"
                    + sp + "Metro Code" + sp + "Subdivision" + sp + "Time Zone" + sp + "Country" + sp + "Continent\n" +
                    "----------" + sp + "----" + sp + "------" + sp + "--------" + sp + "---------" + sp + "-----------"
                    + sp + "----------" + sp + "-----------" + sp + "---------" + sp + "-------" + sp + "---------")


    rdap_header = ("\nIP Address" + rp + "ASN" + rp + "ASN CIDR" + rp + "ASN Country Code" + rp + "ASN Date" + rp +
                   "ASN Description" + rp + "ASN Registry\n" +
                   "----------" + rp + "---" + rp + "--------" + rp + "----------------" + rp + "--------" + rp +
                   "---------------" + rp + "------------")

    # If GeoIP and RDAP dicts are empty
    if not geoip and not rdap:
        return no_geoip + "\n" + no_rdap

    # If RDAP dict is empty
    if not rdap:
        output = ''.join([output, geoip_header + "\n"])

        for key, value in geoip.items():
            output = ''.join([output, key + '{:>10}'.format('')])
            for item in value:
                output = ''.join([output, '{:>20}'.format(str(item))])

            output = ''.join([output, "\n\n"])
            output = ''.join([output, no_rdap])

        return output

    # If GeoIP dict is empty
    if not geoip:
        output = ''.join([output, rdap_header + "\n"])

        for key, value in rdap.items():
            output = ''.join([output, key + '{:>10}'.format('')])
            for item in value:
                output = ''.join([output, '{:>24}'.format(str(item))])

            output = ''.join([output, "\n\n"])
            output = ''.join([output, no_geoip])

        return output

    # If GeoIP and RDAP dicts are not empty; that is, not an edge case
    output = ''.join([output, geoip_header + "\n"])
    for key, value in geoip.items():
        output = ''.join([output, key + '{:>10}'.format('')])
        for item in value:
            output = ''.join([output, '{:<15}'.format(str(item))])

        output = ''.join([output, "\n"])

    output = ''.join([output, "\n" + rdap_header + "\n"])
    for key, value in rdap.items():
        output = ''.join([output, key + '{:>10}'.format('')])
        for item in value:
            output = ''.join([output, '{:<15}'.format(str(item))])

        output = ''.join([output, "\n"])

    return output


def count_valid_addresses(good, bad):
    if good is 1:
        print("1 token matching an IP address was found in file.")

    else:
        print(str(good) + " tokens matching IP addresses were found in file.")

    if bad is 1:
        print("1 token not matching an IP address (junk token) was found in file.\n" +
              "******************************************************************\n\n")

    else:
        print(str(bad) + " tokens not matching IP addresses (junk tokens) were found in file.\n" +
              "************************************************************************\n\n")


def count_valid_results(field, has_data, no_data):
    print("Done.\n")

    if has_data is 1:
        print("Results were found for 1 address.")

    else:
        print("Results were found for " + str(has_data) + " addresses.")

    if no_data is 1:
        print("No results are available for 1 address.\n" +
              "***************************************\n\n")

    else:
        print("No results are available for " + str(no_data) + " addresses.\n" +
              "*****************************************\n\n")


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
        self.assertEqual(["17.0.0.1"], add_valid_addresses_to_list("one_valid_entry.csv"))

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

    def test_list_has_one_good_IPv4_geolite2_match_and_some_junk(self):
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

    def test_list_has_two_good_IPv6_geolite2_matches(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America']},
                         get_geoip_data(["17.0.0.1"]))

    def test_list_has_one_good_IPv4_and_one_good_IPv6_geolite2_match(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America']},
                         get_geoip_data(["17.0.0.1"]))


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


class TestDisplayGeoipAndRdapData(unittest.TestCase):
    geoip_output = ("IP Address           City           Radius           Latitude           Longitude           "
                    + "Postal Code           Metro Code           Subdivision           Time Zone           Country           "
                    + "Continent\n17.0.0.1          Cupertino           1000                37.3042             "
                    + "-122.0946           None                807                 California          America/Los_Angeles "
                    + "United States       North America       ")

    geoip_double_output = (geoip_output + "\n73.78.160.191          Aurora              5                   39.6603" +
                           "             -104.7681           None                751                 Colorado" +
                           "            America/Denver      United States       North America       ")

    rdap_output = ("IP Address                ASN                ASN CIDR                ASN Country Code        " +
                   "        ASN Date                ASN Description                ASN Registry\n" +
                   "74.125.225.229          15169                   74.125.225.0/24         US                   " +
                   "   2007-03-13              GOOGLE - Google LLC, US arin                    ")

    rdap_double_output = (rdap_output + "\n74.125.225.229          15169                   74.125.225.0/24         US                   " +
                   "   2007-03-13              GOOGLE - Google LLC, US arin                    ")

    geoip_dict = {"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California', 'America/Los_Angeles',
                               'United States', 'North America']}

    geoip_double_dict = {"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California', 'America/Los_Angeles',
                               'United States', 'North America'],
                         "73.78.160.191": ['Aurora', 5, 39.6603, -104.7681, None, 751, 'Colorado',
                                            'America/Denver', 'United States', 'North America']}

    rdap_dict = {"74.125.225.229": ['15169', '74.125.225.0/24', 'US', '2007-03-13', 'GOOGLE - Google LLC, US', 'arin'],}

    rdap_double_dict = {"74.125.225.229": ['15169', '74.125.225.0/24', 'US', '2007-03-13', 'GOOGLE - Google LLC, US', 'arin'],
                        "17.0.0.1": ['714', '17.0.0.0/21', 'US', '1990-04-16', 'APPLE-ENGINEERING - Apple Inc., US', 'arin']}

    def test_empty_geoip_dict_and_empty_rdap_dict(self):
        self.assertEqual("No valid GeoIP data was passed in.\nNo valid RDAP data was passed in.",
                         display_geoip_and_rdap_data({}, {}))

    def test_one_geoip_dict_and_empty_rdap_dict(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.geoip_output + "\n\nNo valid RDAP data was passed in.",
                         display_geoip_and_rdap_data(TestDisplayGeoipAndRdapData.geoip_dict, {}))

    def test_empty_geoip_dict_and_one_rdap_dict(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.rdap_output + "\n\nNo valid GeoIP data was passed in.",
                         display_geoip_and_rdap_data({},TestDisplayGeoipAndRdapData.rdap_dict))

    def test_one_good_geoip_dict_and_one_good_rdap_dict(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.geoip_output + "\n\n" + TestDisplayGeoipAndRdapData.rdap_output,
            display_geoip_and_rdap_data(TestDisplayGeoipAndRdapData.geoip_dict, TestDisplayGeoipAndRdapData.rdap_dict))

    def test_two_good_geoip_dicts_and_two_good_rdap_dicts(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.geoip_double_output + "\n\n" + TestDisplayGeoipAndRdapData.rdap_double_output,
            display_geoip_and_rdap_data(TestDisplayGeoipAndRdapData.geoip_double_dict, TestDisplayGeoipAndRdapData.rdap_double_dict))


if __name__ == '__main__':
    # unittest.main()
    main()
