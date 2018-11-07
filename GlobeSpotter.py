import unittest
import ipaddress
import csv
import sys
from geolite2 import geolite2           # pip install maxminddb-geolite2
from ipwhois import IPWhois             # pip install whois
# import whois                          # pip install python-whois
import warnings
import pandas as pd
import datetime
import math


# pip freeze > requirements.txt
# pip install -r requirements.txt

# Good list of sample IPs for testing https://tools.tracemyip.org/search--ip/list

# Before running, terminal <.\venv\Scripts\activate.bat>
# To exit venv, type deactivate

# class GlobeSpotter:
# To run in terminal, python GlobeSpotter.py <filename>

# The following two lines disable warnings by default. To re-enable, run program with -w.
if not sys.warnoptions:
    warnings.simplefilter("ignore")


def main():
    print(display_title())

    file_name = get_file()

    valid_addresses = store_verified_addresses(file_name)

    geoip_data = lookup_geoip(valid_addresses)

    # rdap_data = lookup_rdap(valid_addresses)

    # geoip_and_rdap_values = display_data(geoip_data, rdap_data)
    geoip_and_rdap_values = display_data(geoip_data)

    # exit_options(geoip_and_rdap_values[0], geoip_and_rdap_values[1])
    exit_options(geoip_and_rdap_values[0])


# ASCII art tomfoolery
def display_title():
    welcome = ("\n\n********************************************************************************\n" +
               " ****************************************************************************** \n" +
               "  _____ _       _           _____             _   _" + "                 .-'';'-.\n"
               " / ____| |     | |         / ____|           | | | |" + "              ,'   <_,-.`.\n"
               "| |  __| | ___ | |__   ___| (___  _ __   ___ | |_| |_ ___ _ __" + "   /)   ,--,_>\_\\\n"
               "| | |_ | |/ _ \| '_ \ / _ " + r"\\" + "___ \| '_ \ / _ \| __| __/ _ \ '__|" + " |'   (   x   \_|\n"
               "| |__| | | (_) | |_) |  __/____) | |_) | (_) | |_| ||  __/ |" + "    |_    `-.    / |\n"
               " \_____|_|\___/|_.__/ \___|_____/| .__/ \___/ \__|\__\___|_|" + "     \`-.   ;  _(`/\n"
               "                                 | |" + "                              `.(    \/ ,'\n"
               "                                 |_|" + "                                `-....-'\n" +
               " ****************************************************************************** \n" +
               "********************************************************************************\n\n")

    return welcome


# If a file is not passed in as a command line argument, prompts the user for a file name.
def get_file():
    file_name = input("Please enter the name of a .csv or .log file to be read: ")

    return file_name


# Checks that the given file is valid.
# def check_if_file_name_is_valid(file_name):
#     try:
#         fh = open('file_name', 'r')
#         fh.close()
#         return
#
#     except FileNotFoundError:
    # Keep preset values

    # valid_file = False

    # If file is in immediate folder:
    #   valid_file = True

    # Else:
        # Search recursively for file
        # If file is found:
            # valid_file = True

        # If file is still not found:
            # Prompt for new_file_name
            # check_if_file_name_is_valid(new_file_name)


# Checks if an IP address is valid by querying the ipaddress module. Bad IPs return a ValueError from ipaddress.
def verify_address(ip):
    try:
        potential_address = ipaddress.ip_address(ip)
        return str(potential_address)

    except ValueError:
        return

    except TypeError:
        return


# Parses a .csv file for valid IP addresses and returns them as a list. Ignores any non-valid addresses.
def store_verified_addresses(input_file):
    ip_list = []
    good = 0
    bad = 0

    print("Reading file...", end="", flush=True)

    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            for token in row:
                if verify_address(token) is not None:
                    ip_list.append(token)
                    good += 1
                else:
                    bad += 1

    print(" Done.\n" + "********************\n\n")

    count_addresses(good, bad)

    return ip_list


# Iterates through a list of valid IP addresses and returns GeoIP location data as a dictionary value.
def lookup_geoip(ip_list):
    geoip_data = {}
    reader = geolite2.reader()

    has_data = 0
    no_data = 0

    print("Looking up GeoIP (location) data...", end="", flush=True)

    # If ip_list is empty, stop doing work
    if not ip_list:
        count_results("GeoIP", has_data, no_data)

        geoip_data.update({"No valid IP addresses.": ["None", "None", "None", "None", "None", "None", "None", "None",
                                                      "None", "None"]})

        return geoip_data

    for ip in ip_list:
        data_list = []

        try:
            match = reader.get(ip)

            if match is None:
                geoip_data.update(
                    {"No data": ["No data", "No data", "No data", "No data", "No data", "No data", "No data",
                                 "No data", "No data", "No data"]})

                no_data += 1
                continue
                # return geoip_data

            # City                  -> {'city': {'names': {'en': value}}
            data_list.append(match.get('city', {}).get('names', {}).get('en'))

            # Accuracy radius       -> {'location': {'longitude': value}}
            data_list.append(match.get('location', {}).get('accuracy_radius'))

            # Latitude              -> {'location': {'latitude': value}}
            data_list.append(match.get('location', {}).get('latitude'))

            # Longitude             -> {'location': {'longitude': value}}
            data_list.append(match.get('location', {}).get('longitude'))

            # Postal code           -> {'postal': {'code': value}}
            data_list.append(match.get('postal', {}).get('code'))

            # Metro code            -> {'location': {'metro_code': value}}
            data_list.append(str(match.get('location', {}).get('metro_code')))

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
            geoip_data.update({"No data": ["No data", "No data", "No data", "No data", "No data", "No data", "No data",
                                           "No data", "No data", "No data"]})

    count_results("GeoIP", has_data, no_data)

    geolite2.close()

    return geoip_data


# def lookup_rdap(ip_list):
    # rdap_data = {}
    # has_data = 0
    # no_data = 0
    #
    # print("Looking up RDAP (internet service provider) data.\n" +
    #       "Depending on the number of valid IP tokens, this may take some time...", end="", flush=True)
    #
    # # If ip_list is empty, stop doing work
    # if not ip_list:
    #     count_results("RDAP", has_data, no_data)
    #
    #     rdap_data.update({"No data.": ["No data", "No data", "No data", "No data", "No data", "No data"]})
    #
    #     return rdap_data
    #
    # for ip in ip_list:
    #     try:
    #         data_list = []
    #         obj = IPWhois(ip)
    #         results = obj.lookup_rdap(depth=1)
    #
    #         data_list.append(results.get('asn'))
    #         data_list.append(results.get('asn_cidr'))
    #         data_list.append(results.get('asn_country_code'))
    #         data_list.append(results.get('asn_date'))
    #         data_list.append(results.get('asn_description'))
    #         data_list.append(results.get('asn_registry'))
    #
    #         rdap_data.update({ip: data_list})
    #
    #         has_data += 1
    #         print('.', end="", flush=True)
    #
    #     except:
    #         rdap_data.update({ip: ["No data", "No data", "No data", "No data", "No data", "No data"]})
    #         no_data += 1
    #         print('.', end="", flush=True)
    #
    # count_results("RDAP", has_data, no_data)
    #
    # return rdap_data


# TODO put edge cases as separate methods; I don't like the clutter of this method.
# def display_data(geoip, rdap):
def display_data(geoip):
    geoip_header = ["IP Address", "City", "Radius", "Latitude", "Longitude", "Postal Code", "Metro Code",
                    "Region", "Time Zone", "Country", "Continent"]

    rdap_header = ["IP Address", "ASN", "Supernet", "Country Code", "ASN Date", "Description", "Registry"]

    no_geoip = "No valid GeoIP data was passed in."
    no_rdap = "No valid RDAP data was passed in."

    geoip_data_set = []
    rdap_data_set = []

    for key, value in geoip.items():
        temp_list = [key]
        for item in value:
            temp_list.append(item)

        geoip_data_set.append(temp_list)

    geoip_dataframe = pd.DataFrame(data=geoip_data_set, columns=geoip_header)
    print(geoip_dataframe)
    print()

    # for key, value in rdap.items():
    #     temp_list = [key]
    #     for item in value:
    #         temp_list.append(item)
    #
    #     rdap_data_set.append(temp_list)
    #
    # rdap_dataframe = pd.DataFrame(data=rdap_data_set, columns=rdap_header)
    # print(rdap_dataframe)
    # print()

    # return [geoip_dataframe, rdap_dataframe]

    return [geoip_dataframe]


def count_addresses(good, bad):
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


def count_results(field, has_data, no_data):
    print("Done.\n")

    if has_data is 1:
        print(field + " results were found for 1 address.")

    else:
        print(field + " results were found for " + str(has_data) + " addresses.")

    if no_data is 1:
        print("No " + field + " results are available for 1 address.\n" +
              "***************************************\n\n")

    else:
        print("No " + field + " results are available for " + str(no_data) + " addresses.\n" +
              "*****************************************\n\n")


# def exit_options(geoip_dataframe, rdap_dataframe):
def exit_options(geoip_dataframe):
    menu = ("\n[R] to read a new file\n" +
            "[S] to search results\n" +
            "[O] to sort results\n" +
            "[N] to count results\n" +
            "[C] to output current results as .csv\n" +
            "[J] to output current results as a JSON object\n" +
            "[X] or [Enter] to exit: ")

    choice = input(menu)

    while choice not in 'rsoncjx':
        choice = input(choice + "\n is not a valid input\n" + menu)

    if choice is 'r':
        main()

    elif choice is 's':
        search_results(geoip_dataframe)

    elif choice is 'o':
        sort_results(geoip_dataframe)

    elif choice is 'n':
        final_counter(geoip_dataframe)

    elif choice is 'c':
        # output_csv(geoip_dataframe, rdap_dataframe)
        output_csv(geoip_dataframe)

    elif choice is 'j':
        # output_json(geoip_dataframe, rdap_dataframe)
        output_json(geoip_dataframe)

    elif choice is 'x':
        exit()

    return


# def output_csv(geoip_results, rdap_results):
def output_csv(geoip_results):
    timestamp = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    filename = "GlobeSpotter_results" + timestamp + ".csv"

    geoip_results.to_csv(filename)
    # rdap_results.to_csv(filename, mode='a')

    print("All results outputted to " + filename)

    return


# def output_json(geoip_results, rdap_results):
def output_json(geoip_results):
    pass


def search_results(geoip_results):
    geoip_header = ["IP address", "City", "Radius", "Latitude", "Longitude", "Postal Code", "Metro Code",
                    "Region", "Time Zone", "Country", "Continent"]

    column = input("\nPlease select a column to search in, or [X] to return to menu.\n" +
                   "Valid columns are " + str(geoip_header) + ": ")

    if column == 'x':
        exit_options(geoip_results)

    while column not in geoip_header:
        column = input("\nInvalid entry. Valid columns are " + str(geoip_header))

    value = input("Please enter a value to search for, or [X] to return to menu: ")

    if value == 'x':
        exit_options(geoip_results)

    results_dataframe = geoip_results[geoip_results[column].notnull() & (geoip_results[column] == value)]

    if results_dataframe.empty:
        print("\nNo results found in " + str(column) + " for " + str(value) + ".")
        print("\n")

        exit_options(geoip_results)

    else:
        print(results_dataframe)
        print("\n")

        exit_options(geoip_results)


def sort_results(geoip_results):
    geoip_header = ["IP Address", "City", "Radius", "Latitude", "Longitude", "Postal Code", "Metro Code",
                    "Region", "Time Zone", "Country", "Continent"]

    column = input("\nPlease select a column to sort by, or [X] to return to menu.\n" +
                   "Valid columns are " + str(geoip_header) + ": ")

    if column == 'x':
        exit_options(geoip_results)

    while column not in geoip_header:
        column = input("\nInvalid entry. Valid columns are " + str(geoip_header)).capitalize()

    results_dataframe = geoip_results.sort_values(by=[column])

    print(results_dataframe)
    print("\n")

    exit_options(geoip_results)


def final_counter(geoip_results):
    geoip_header = ["IP Address", "City", "Radius", "Latitude", "Longitude", "Postal Code", "Metro Code",
                    "Region", "Time Zone", "Country", "Continent"]

    column = input("\nThis function allows at-a-glance interpretation of data by counting repeated values.\n" +
                   "Please select a column to count by, or [X] to exit.\n" +
                   "Valid columns are " + str(geoip_header) + ": ")

    print("\n")

    if column == 'x':
        exit_options(geoip_results)

    while column not in geoip_header:
        column = input("\nInvalid entry. Valid columns are " + str(geoip_header)).capitalize()

    results_dataframe = geoip_results[column].value_counts()

    print(results_dataframe)
    print("\n")

    exit_options(geoip_results)


class TestCheckIfValidAddress(unittest.TestCase):
    def test_IPv4_address_is_valid(self):
        self.assertEqual("192.168.0.1", verify_address('192.168.0.1'))

    def test_IPv6_address_is_valid(self):
        self.assertEqual("2001:db:8::", verify_address('2001:db:8::'))

    def test_IP_address_is_not_valid(self):
        self.assertEqual(None, verify_address("Foobar"))


class TestAddValidAddressesToList(unittest.TestCase):
    def test_empty_file(self):
        self.assertEqual([], store_verified_addresses("empty_file.csv"))

    def test_file_with_no_valid_entries(self):
        self.assertEqual([], store_verified_addresses("no_valid_entries.csv"))

    def test_file_with_one_valid_entry(self):
        self.assertEqual(["17.0.0.1"], store_verified_addresses("one_valid_entry.csv"))

    def test_file_with_one_valid_entry_and_some_junk(self):
        self.assertEqual(["192.168.0.1"], store_verified_addresses("one_valid_entry_and_some_junk.csv"))

    def test_file_with_one_row_of_valid_entry_and_some_junk(self):
        self.assertEqual(["192.168.0.1"], store_verified_addresses("one_row_of_valid_entry_and_some_junk.csv"))

    def test_file_with_two_rows_of_valid_entries(self):
        self.assertEqual(['192.168.0.1', '2001:db:8::', '2001:db:8::', '192.168.0.1'],
                         store_verified_addresses("two_rows_of_valid_entries.csv"))

    def test_file_with_two_rows_of_valid_entries_and_some_junk(self):
        self.assertEqual(["192.168.0.1", "192.168.0.1", "2001:db:8::"],
                         store_verified_addresses("two_rows_of_valid_entries_and_some_junk.csv"))

    def test_file_with_several_rows_of_valid_entries_and_some_junk(self):
        self.assertEqual(["192.168.0.1", "192.168.0.1", "192.168.0.1", "2001:db:8::", "192.168.0.1", "2001:db:8::",
                          "192.168.0.1", "192.168.0.1", "192.168.0.1", "2001:db:8::", "192.168.0.1", "2001:db:8::",
                          "192.168.0.1", "192.168.0.1", "192.168.0.1", "2001:db:8::", "192.168.0.1", "2001:db:8::"],
                         store_verified_addresses("several_rows_of_valid_entries_and_some_junk.csv"))


class TestGetGeoipData(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual({"No valid IP addresses.":
                              ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         lookup_geoip([]))

    def test_list_is_all_junk(self):
        self.assertEqual({"No GeoIP/location data available for this IP.":
                              ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         lookup_geoip(["Foobar"]))

    # def test_list_has_one_IPv4_geolite2_match_with_no_available_data(self):
    #     self.assertEqual({"No data available.":
    #                                 ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
    #                      lookup_geoip(["17.0.0.0"]))

    def test_list_has_one_good_IPv4_geolite2_match(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America']},
                         lookup_geoip(["17.0.0.1"]))

    def test_list_has_one_IPv6_geolite2_match_with_no_available_data(self):
        self.assertEqual({"No data available in geolite2.":
                                    ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         lookup_geoip(["2001:db:8::"]))

    # TODO IPv6 addresses aren't returning geolite2 results. Problem with my code, the database, or the IP addresses?
    # def test_list_has_one_good_IPv6_geolite2_match(self):
    #     self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
    #                                    'America/Los_Angeles', 'United States', 'North America']},
    #                      lookup_geoip(["2001:4860:0:2001::68"]))

    def test_list_has_one_good_IPv4_geolite2_match_and_some_junk(self):
        self.assertEqual({"No GeoIP/location data available for this IP.":
                            ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"],
                          "17.0.0.1":
                            ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California', 'America/Los_Angeles',
                             'United States', 'North America'],
                          "No GeoIP/location data available for this IP.":
                            ["None", "None", "None", "None", "None", "None", "None", "None", "None", "None"]},
                         lookup_geoip(["Foobar", "17.0.0.1", "Barfoo"]))

    def test_list_has_two_good_IPv4_geolite2_matches(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America'],
                          "73.78.160.191": ['Aurora', 5, 39.6603, -104.7681, None, 751, 'Colorado',
                                            'America/Denver', 'United States', 'North America']},
                         lookup_geoip(["17.0.0.1", "73.78.160.191"]))

    def test_list_has_two_good_IPv6_geolite2_matches(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America']},
                         lookup_geoip(["17.0.0.1"]))

    def test_list_has_one_good_IPv4_and_one_good_IPv6_geolite2_match(self):
        self.assertEqual({"17.0.0.1": ['Cupertino', 1000, 37.3042, -122.0946, None, 807, 'California',
                                       'America/Los_Angeles', 'United States', 'North America']},
                         lookup_geoip(["17.0.0.1"]))


class TestGetRdapData(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual({"No valid IP addresses.":
                            ["None", "None", "None", "None", "None", "None"]},
                         lookup_rdap([]))

    def test_list_has_one_good_IPv4_whois_match(self):
        self.assertEqual({"74.125.225.229":
                            ['15169', '74.125.225.0/24', 'US', '2007-03-13', 'GOOGLE - Google LLC, US', 'arin']},
                         lookup_rdap(['74.125.225.229']))

    def test_list_has_two_good_IPv4_whois_matches(self):
        self.assertEqual({"74.125.225.229":
                            ['15169', '74.125.225.0/24', 'US', '2007-03-13', 'GOOGLE - Google LLC, US', 'arin'],
                          "17.0.0.1":
                              ['714', '17.0.0.0/21', 'US', '1990-04-16', 'APPLE-ENGINEERING - Apple Inc., US', 'arin']
                          },
                         lookup_rdap(['74.125.225.229', '17.0.0.1']))

    def test_list_has_one_good_IPv6_whois_match(self):
        self.assertEqual({"2001:4860:0:2001::68":
                            ['15169', '2001:4860::/32', 'US', '2005-03-14', 'GOOGLE - Google LLC, US', 'arin']},
                         lookup_rdap(['2001:4860:0:2001::68']))


class TestDisplayGeoipAndRdapData(unittest.TestCase):
    geoip_output = ("Ip address           City           Radius           Latitude           Longitude           "
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
                         display_data({}, {}))

    def test_one_geoip_dict_and_empty_rdap_dict(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.geoip_output + "\n\nNo valid RDAP data was passed in.",
                         display_data(TestDisplayGeoipAndRdapData.geoip_dict, {}))

    def test_empty_geoip_dict_and_one_rdap_dict(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.rdap_output + "\n\nNo valid GeoIP data was passed in.",
                         display_data({}, TestDisplayGeoipAndRdapData.rdap_dict))

    def test_one_good_geoip_dict_and_one_good_rdap_dict(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.geoip_output + "\n\n" + TestDisplayGeoipAndRdapData.rdap_output,
                         display_data(TestDisplayGeoipAndRdapData.geoip_dict, TestDisplayGeoipAndRdapData.rdap_dict))

    def test_two_good_geoip_dicts_and_two_good_rdap_dicts(self):
        self.assertEqual(TestDisplayGeoipAndRdapData.geoip_double_output + "\n\n" + TestDisplayGeoipAndRdapData.rdap_double_output,
                         display_data(TestDisplayGeoipAndRdapData.geoip_double_dict, TestDisplayGeoipAndRdapData.rdap_double_dict))


if __name__ == '__main__':
    # unittest.main()
    main()
