#!/usr/bin/env python3

# Copyright 2022 Blacki
# Thanks to Ris for the contents of the LANG_SUFFIXES variable (possible wiki language suffixes).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import math
from enum import Enum
import ipaddress
import itertools
import json
from operator import itemgetter
import requests
import sys
import time
import tldextract
from urllib.parse import urlparse
import validators

LANG_SUFFIXES = ('/ab', '/abs', '/ace', '/ady', '/ady-cyrl', '/aeb', '/aeb-arab', '/aeb-latn', '/af', '/ak', '/aln',
                 '/alt', '/am', '/ami', '/an', '/ang', '/anp', '/ar', '/arc', '/arn', '/arq', '/ary', '/arz', '/as',
                 '/ase', '/ast', '/atj', '/av', '/avk', '/awa', '/ay', '/az', '/azb', '/ba', '/ban', '/bar', '/bbc',
                 '/bbc-latn', '/bcc', '/bcl', '/be', '/be-tarask', '/bg', '/bgn', '/bh', '/bho', '/bi', '/bjn', '/bm',
                 '/bn', '/bo', '/bpy', '/bqi', '/br', '/brh', '/bs', '/btm', '/bto', '/bug', '/bxr', '/ca', '/cbk-zam',
                 '/cdo', '/ce', '/ceb', '/ch', '/chr', '/chy', '/ckb', '/co', '/cps', '/cr', '/crh', '/crh-cyrl',
                 '/crh-latn', '/cs', '/csb', '/cu', '/cv', '/cy', '/da', '/de', '/de-at', '/de-ch', '/de-formal',
                 '/default', '/din', '/diq', '/dsb', '/dtp', '/dty', '/dv', '/dz', '/ee', '/egl', '/el', '/eml', '/en',
                 '/en-ca', '/en-gb', '/eo', '/es', '/es-formal', '/et', '/eu', '/ext', '/fa', '/ff', '/fi', '/fit',
                 '/fj', '/fo', '/fr', '/frc', '/frp', '/frr', '/fur', '/fy', '/ga', '/gag', '/gan', '/gan-hans',
                 '/gan-hant', '/gcr', '/gd', '/gl', '/glk', '/gn', '/gom', '/gom-deva', '/gom-latn', '/gor', '/got',
                 '/grc', '/gsw', '/gu', '/gv', '/ha', '/hak', '/haw', '/he', '/hi', '/hif', '/hif-latn', '/hil', '/hr',
                 '/hrx', '/hsb', '/ht', '/hu', '/hu-formal', '/hy', '/hyw', '/ia', '/id', '/ie', '/ig', '/ii', '/ik',
                 '/ike-cans', '/ike-latn', '/ilo', '/inh', '/io', '/is', '/it', '/iu', '/ja', '/jam', '/jbo', '/jut',
                 '/jv', '/ka', '/kaa', '/kab', '/kbd', '/kbd-cyrl', '/kbp', '/kg', '/khw', '/ki', '/kiu', '/kjp', '/kk',
                 '/kk-arab', '/kk-cn', '/kk-cyrl', '/kk-kz', '/kk-latn', '/kk-tr', '/kl', '/km', '/kn', '/ko', '/ko-kp',
                 '/koi', '/krc', '/kri', '/krj', '/krl', '/ks', '/ks-arab', '/ks-deva', '/ksh', '/ku', '/ku-arab',
                 '/ku-latn', '/kum', '/kv', '/kw', '/ky', '/la', '/lad', '/lb', '/lbe', '/lez', '/lfn', '/lg', '/li',
                 '/lij', '/liv', '/lki', '/lld', '/lmo', '/ln', '/lo', '/loz', '/lrc', '/lt', '/ltg', '/lus', '/luz',
                 '/lv', '/lzh', '/lzz', '/mai', '/map-bms', '/mdf', '/mg', '/mhr', '/mi', '/min', '/mk', '/ml', '/mn',
                 '/mni', '/mnw', '/mo', '/mr', '/mrj', '/ms', '/mt', '/mwl', '/my', '/myv', '/mzn', '/na', '/nah',
                 '/nan', '/nap', '/nb', '/nds', '/nds-nl', '/ne', '/new', '/niu', '/nl', '/nl-informal', '/nn', '/nov',
                 '/nqo', '/nrm', '/nso', '/nv', '/ny', '/nys', '/oc', '/olo', '/om', '/or', '/os', '/pa', '/pag',
                 '/pam', '/pap', '/pcd', '/pdc', '/pdt', '/pfl', '/pi', '/pih', '/pl', '/pms', '/pnb', '/pnt', '/prg',
                 '/ps', '/pt', '/pt-br', '/qqq', '/qu', '/qug', '/rgn', '/rif', '/rm', '/rmy', '/ro', '/roa-tara',
                 '/ru', '/rue', '/rup', '/ruq', '/ruq-cyrl', '/ruq-latn', '/rw', '/sa', '/sah', '/sat', '/sc', '/scn',
                 '/sco', '/sd', '/sdc', '/sdh', '/se', '/sei', '/ses', '/sg', '/sgs', '/sh', '/shi', '/shn',
                 '/shy-latn', '/si', '/sk', '/skr', '/skr-arab', '/sl', '/sli', '/sm', '/sma', '/smn', '/sn', '/so',
                 '/sq', '/sr', '/sr-ec', '/sr-el', '/srn', '/ss', '/st', '/stq', '/sty', '/su', '/sv', '/sw', '/szl',
                 '/szy', '/ta', '/tay', '/tcy', '/te', '/tet', '/tg', '/tg-cyrl', '/tg-latn', '/th', '/ti', '/tk',
                 '/tl', '/tly', '/tn', '/to', '/tpi', '/tr', '/tru', '/trv', '/ts', '/tt', '/tt-cyrl', '/tt-latn',
                 '/tw', '/ty', '/tyv', '/tzm', '/udm', '/ug', '/ug-arab', '/ug-latn', '/uk', '/ur', '/uz', '/ve',
                 '/vec', '/vep', '/vi', '/vls', '/vmf', '/vo', '/vot', '/vro', '/wa', '/war', '/wo', '/wuu', '/xal',
                 '/xh', '/xmf', '/xsy', '/yi', '/yo', '/yue', '/za', '/zea', '/zgh', '/zh', '/zh-cn', '/zh-hans',
                 '/zh-hant', '/zh-hk', '/zh-mo', '/zh-my', '/zh-sg', '/zh-tw', '/zu')

API_ENDPOINT = "https://wiki.gentoo.org/api.php"

HTTP_HEADERS = {
    "Accept-Encoding": "gzip",
    "User-Agent": "BlackiBot/1.1 (https://wiki.gentoo.org/wiki/User:Blacki) Python/3.10.4 Requests/2.25.1"
}

# Note: With this request, the API returns results
#       sorted by page id, not by page title.
URL_PARAMETERS = {
    "action": "query",
    "ellimit": "max",
    "errorformat": "plaintext",
    "format": "json",
    "formatversion": "2",
    "gapfilterredir": "nonredirects",
    "gaplimit": "max",
    "gapnamespace": "0",
    "generator": "allpages",
    "maxlag": 5,
    "prop": "extlinks"
}

# Contains the JSON-formatted list of links to be tested.
DUMP_FILE = "dump.json"
# Contains the MediaWiki-formatted list of valid HTTP external links that (may) have an HTTPS version.
RESULT_NOHTTPS_FILE = "result_nohttps.mediawiki"
# Contains the MediaWiki-formatted list of broken HTTP(S) external links.
RESULT_BROKEN_FILE = "result_broken.mediawiki"

class TestResult(Enum):
    CHUNKEDENCODINGERROR = "Chunked encoding error"        
    CONNECTIONERROR = "Connection error"
    CONNECTTIMEOUT = "Connect timeout"
    CONTENTDECODINGERROR = "Content decoding error"
    INVALIDURL = "Invalid URL"
    HTTPOK = "OK"
    HTTPNOK = "HTTP non-OK response"
    READTIMEOUT = "Read timeout"
    REQUESTEXCEPTION = "Request exception"
    SPECIALURL = "OK"
    TOOMANYREDIRECTS = "Too many redirects"
    NOHTTPS_HTTPS_CHUNKEDENCODINGERROR = f"HTTPS available, but \"{CHUNKEDENCODINGERROR}\" when requested"
    NOHTTPS_HTTPS_CONNECTIONERROR = "OK"
    NOHTTPS_HTTPS_CONNECTTIMEOUT = f"HTTPS maybe available, but \"{CONNECTTIMEOUT}\" when requested"
    NOHTTPS_HTTPS_CONTENTDECODINGERROR = f"HTTPS available, but \"{CONTENTDECODINGERROR}\" when requested"
    NOHTTPS_HTTPS_HTTPOK = "HTTPS available"
    NOHTTPS_HTTPS_HTTPNOK = f"HTTPS available, but \"{HTTPNOK}\" when requested"
    NOHTTPS_HTTPS_READTIMEOUT = f"HTTPS maybe available, but \"{READTIMEOUT}\" when requested"
    NOHTTPS_HTTPS_REQUESTEXCEPTION = f"HTTPS maybe available, but \"{REQUESTEXCEPTION}\" when requested"
    NOHTTPS_HTTPS_TOOMANYREDIRECTS = f"HTTPS available, but \"{TOOMANYREDIRECTS}\" when requested"

#
# Handles arguments.
#

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, "Error while handling arguments : %s.\n" % message)

parser = MyArgumentParser(description="Audits HTTP(S) external links from english pages in the \"(Main)\" namespace of the Gentoo wiki, and saves results into files (see \"Filenames options\").",
                          add_help=False)

general_group = parser.add_argument_group("General options")
general_group.add_argument("-h", "--help",
                           action="help",
                           help="Shows this help message and exits.")
general_group.add_argument("--from-dump-file",
                           metavar="FILE",
                           help="Uses %(metavar)s as the source of data for the links to be tested, instead of the MediaWiki Action API.")
general_group.add_argument("--wait-time",
                           metavar="DELAY",
                           type=int,
                           default=10,
                           help="The wait time in seconds between network requests on the same host. (default: 10)")

filenames_group = parser.add_argument_group("Filenames options")
filenames_group.add_argument("--dump-file",
                             metavar="FILE",
                             default=DUMP_FILE,
                             help=f"The JSON-formatted dump file in which will be saved the list of links to be tested. (default: \"%(default)s\")")
filenames_group.add_argument("--result-nohttps-file",
                             metavar="FILE",
                             default=RESULT_NOHTTPS_FILE,
                             help=f"The MediaWiki-formatted result file in which will be saved the list of valid HTTP external links that (may) have an HTTPS version. (default: \"%(default)s\")")
filenames_group.add_argument("--result-broken-file",
                             metavar="FILE",
                             default=RESULT_BROKEN_FILE,
                             help=f"The MediaWiki-formatted result file in which will be saved the list of broken HTTP(S) external links. (default: \"%(default)s\")")

args = parser.parse_args()

if args.wait_time < 0:
    parser.print_usage()
    print(f"Error while handling arguments : argument --wait-time: invalid positive or null int value: '{args.wait_time}'.")
    sys.exit(1)

#
# Creates/truncates output files.
#

for output_file in [args.dump_file, args.result_nohttps_file, args.result_broken_file]:
    if output_file == args.dump_file \
   and args.from_dump_file:
        continue

    try:
        f = open(output_file, "w", encoding="utf-8")
    except OSError as e:
        print(f"Error while opening \"{output_file}\" : {e.strerror}")
        sys.exit(1)
    with f:
        pass

#
# Gets links.
#

session = requests.Session()

# A list of lists, of the form :
#   [[<page title>, [<external link URL>, ...]], ...]
wiki_pages_clean = []

pages_count_raw = 0
extlinks_count_raw = 0

if args.from_dump_file:
    print(f"----- Getting links by loading data from file ({args.from_dump_file}) ...")

    try:
        f = open(args.from_dump_file, "r", encoding="utf-8")
    except OSError as e:
        print(f"        Error while opening \"{args.from_dump_file}\" : {e.strerror}")
        sys.exit(1)
    with f:
        wiki_pages_clean = json.load(f)

    pages_count_raw = len(wiki_pages_clean)
    extlinks_count_raw = len(list(itertools.chain.from_iterable([page[1] for page in wiki_pages_clean])))
    
    print(f"        Loaded data for {pages_count_raw} wiki pages ({extlinks_count_raw} HTTP(S) external links) in total.")
else:
    print(f"----- Getting links by fetching data from MediaWiki Action API ({API_ENDPOINT}) ...")

    #
    # Gets data.
    #

    # A dictionary of dictionaries, of the form :
    #   {<page id>: {"title": <page title>, "extlinks": [<external link URL>, ...]}, ...}
    # Note: This is used here instead of a list of lists of the form
    #       [[<page id>, <page title>, [<external link URL>, ...]], ...] for
    #       performance reasons, as the script very frequently needs to
    #       search for a page id (for existence + for access) in the data.
    #       In practice, compared to this other format,
    #       it means that wiki_pages uses 5 times more memory,
    #       but is 100 times faster to access an element by page id,
    #       and is 100 times faster to check for a page id existence.
    wiki_pages = {}

    request_number = 0

    has_continue_keys = True
    previous_continue_keys = []

    while has_continue_keys:
        result = None
        http_status_code = None

        #
        # Requests the API.
        #

        try:
            response = session.get(url=API_ENDPOINT, params=URL_PARAMETERS, headers=HTTP_HEADERS, timeout=5)
        except requests.exceptions.ConnectTimeout:
            result = TestResult.CONNECTTIMEOUT
        except requests.exceptions.ReadTimeout:
            result = TestResult.READTIMEOUT
        except requests.exceptions.ConnectionError:
            result = TestResult.CONNECTIONERROR
        except requests.exceptions.ContentDecodingError:
            result = TestResult.CONTENTDECODINGERROR
        except requests.exceptions.ChunkedEncodingError:
            result = TestResult.CHUNKEDENCODINGERROR
        except requests.exceptions.TooManyRedirects:
            result = TestResult.TOOMANYREDIRECTS
        except requests.exceptions.RequestException:
            result = TestResult.REQUESTEXCEPTION
        else:
            http_status_code = response.status_code
            result = TestResult.HTTPNOK if http_status_code != 200 else TestResult.HTTPOK

        #
        # Handles the request result.
        #

        if result != TestResult.HTTPOK:
            result_s = result.value if result != TestResult.HTTPNOK else f"HTTP {http_status_code}"
            print(f"        Error while requesting {API_ENDPOINT} : {result_s}.")
            sys.exit(1)

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"        Error while requesting {API_ENDPOINT} : invalid JSON response.")
            sys.exit(1)

        # Checks whether the API indicates that
        # there was a problem with the request's URL parameters
        # or more generally with the usage of the API.
        for errwarn_key in ["errors", "warnings"]:
            if errwarn_key in data:
                if len(data[errwarn_key]) > 1:
                    print(f"        Errors while requesting {API_ENDPOINT} : API {errwarn_key} :")
                    for errwarn in data[errwarn_key]:
                        print(f"            {errwarn['text']}")
                else:
                    print(f"        Error while requesting {API_ENDPOINT} : API {errwarn_key[:-1]} : {data[errwarn_key][0]['text']}")
                sys.exit(1)

        request_number += 1

        # Stores relevant data.
        for page in data["query"]["pages"]:
            if not page["pageid"] in wiki_pages:
                wiki_pages[page["pageid"]] = {
                    "title": page["title"],
                    "extlinks": [extlink["url"] for extlink in page.get("extlinks", [])]
                }
                
                pages_count_raw += 1
            else:
                if "extlinks" in page:
                    wiki_pages[page["pageid"]]["extlinks"] += [extlink["url"] for extlink in page["extlinks"]]
        
            extlinks_count_raw += len([extlink["url"] for extlink in page.get("extlinks", [])])

        # Checks whether the API indicates that there are
        # remaining data not yet sent because of response size limits.
        if (has_continue_keys := "continue" in data):
            #
            # Modifies the URL parameters so that the next request tells
            # the API to send remaining data for the initial request.
            #

            for key in previous_continue_keys:
                del URL_PARAMETERS[key]
            
            previous_continue_keys.clear()
            
            for key, value in data["continue"].items():
                URL_PARAMETERS[key] = value
                previous_continue_keys.append(key)

            print(f"        Fetched data for {pages_count_raw} wiki pages ({extlinks_count_raw} external links) so far.")

            #
            # Ensures enough time has passed
            # before the next request to this host.
            #

            print(f"        Waiting {args.wait_time} seconds before the next request (n° {request_number + 1}) ", end="", flush=True)
            for i in range(args.wait_time):
                time.sleep(1)
                print(".", end="", flush=True)
            print("\n", end="", flush=True)
        else:
            print(f"        Fetched data for {pages_count_raw} wiki pages ({extlinks_count_raw} external links) in total.")

    #
    # Cleans data.
    #

    print("----- Cleaning data ...")

    # Converts data into a more suitable format for the remaining of the script.
    wiki_pages_clean = [[value["title"], value["extlinks"]] for key, value in wiki_pages.items()]

    # Sorts data by wiki page title.
    wiki_pages_clean.sort(key=itemgetter(0))

    # Removes wiki pages that are translations.
    wiki_pages_clean = [page for page in wiki_pages_clean if not page[0].endswith(LANG_SUFFIXES)]

    # Removes external links that are not HTTP(S).
    wiki_pages_clean = [[page[0], [url for url in page[1] if (url.startswith("http://") or url.startswith("https://"))]] for page in wiki_pages_clean]
    # Removes pages that don't have external links anymore because of the removal just above.
    wiki_pages_clean = [page for page in wiki_pages_clean if page[1] != []]

    print(f"        Cleaned.")

    #
    # Saves data into file.
    #

    print(f"----- Saving data into file {args.dump_file} ...")

    try:
        f = open(args.dump_file, "w", encoding="utf-8")
    except OSError as e:
        print(f"        Error while opening \"{args.dump_file}\" : {e.strerror}")
        sys.exit(1)
    with f:
        json.dump(wiki_pages_clean, f, indent=4)

    print("        Saved.")

#
# Initializes the variables that will be used when testing links.
#

# A dictionary of lists, of the form :
#   {<host's domain name or IP>: [<last request date>, [<external link URLs from the same host>]], ...}
# <host's domain name or IP> is only the domain + suffix, without the subdomain(s).
# Note: This means that a.b.example.com and c.d.example.com
#       are considered the same host.
hosts = {}
# A list of lists, of the form :
#   [[<host's domain name or IP>, [<external link URLs from the same host>], <last request date>], ...]
# Lists are sorted by decreasing list length.
hosts_sorted = []
# A dictionary of strings, of the form :
#   {<external link's URL>: <test result string>, ...}
broken_extlinks = {}
# A dictionary of strings, of the form :
#   {<external link's URL>: <test result string>, ...}
nohttps_extlinks = {}
# A dictionary of strings, of the form :
#   {<external link's URL>: <test result string>, ...}
special_extlinks = {}

# Gets the list of links.
extlinks = list(itertools.chain.from_iterable([page[1] for page in wiki_pages_clean]))
extlinks_count_raw = len(extlinks)
# Removes duplicates from the list.
extlinks = list(set(extlinks))
extlinks_count_unique = len(extlinks)

# Fills "hosts" variable, and takes care of some special cases.
for extlink in extlinks:
    hostname = urlparse(extlink).hostname

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        hostname_is_ip = 0
    else:
        hostname_is_ip = 1

    # Checks whether this is a non[-always]-reachable link
    # ("localhost" + multicast/link-local/private/loopback/reserved/... IPs).
    # Note: Without this, it may otherwise be recognised as invalid URL or broken link ;
    #       also, its registered domain wouldn't be extracted correctly.
    if hostname == "localhost" \
    or (hostname_is_ip         \
    and (not ip.is_global or ip.is_multicast)):
        special_extlinks[extlink] = TestResult.SPECIALURL.value
        pass
    # Checks whether this is an invalid URL.
    # Note: Without this, its registered domain wouldn't be extracted correctly.
    elif not validators.url(extlink):
        broken_extlinks[extlink] = TestResult.INVALIDURL.value
    else:
        host = hostname if hostname_is_ip else tldextract.extract(hostname).registered_domain

        if host not in hosts:
            hosts[host] = [0, [extlink]]
        else:
            hosts[host][1].append(extlink)

extlinks_count_tobetested = extlinks_count_unique - len(special_extlinks) - len(broken_extlinks)
digits_count = len(str(extlinks_count_tobetested))

# Fills "hosts_sorted" variable.
hosts_sorted = [[k, v[1], v[0]] for k, v in hosts.items()]
# Sorts the list by decreasing size of links lists.
hosts_sorted.sort(key=lambda host: len(host[1]), reverse=True)

#
# Displays links summary.
#

print("----- Testing links ...")
print(f"        {extlinks_count_raw} HTTP(S) external links.")
print(f"            {round(100*((extlinks_count_raw-extlinks_count_unique)/extlinks_count_raw))} % are duplicates.")
print(f"        {extlinks_count_unique} unique HTTP(S) external links.")
print(f"            {len(special_extlinks)} are special URLs (\"localhost\", multicast IP addresses, private IP addresses, ...).")
print(f"            {len(broken_extlinks)} are invalid URLs.")
print(f"        {extlinks_count_tobetested} unique HTTP(S) external links to be tested.\n")

#
# Tests links.
#

extlinks_count = 0

while True:
    start_time = time.time()

    # Loops over hosts that have links to be tested.
    for host in hosts_sorted:
        extlink = host[1][0]
        result = None
        http_status_code = None
        request_time = time.time()

        # Checks whether not enough time has passed since the last request to the host of the currently tested link.
        if request_time - host[2] < args.wait_time:
            continue

        extlinks_count += 1

        print(f"        [{extlinks_count:>{digits_count}} / {extlinks_count_tobetested}] {extlink} ...")

        #
        # Requests the link's target.
        #

        try:
            # Note: GET requests are used here instead of HEAD requests,
            #       since many servers seem to respond with HTTP 405 ("Method Not Allowed") to them.
            resp = requests.get(extlink, headers=HTTP_HEADERS, timeout=5)
        except requests.exceptions.ConnectTimeout:
            result = TestResult.CONNECTTIMEOUT
        except requests.exceptions.ReadTimeout:
            result = TestResult.READTIMEOUT
        except requests.exceptions.ConnectionError:
            result = TestResult.CONNECTIONERROR
        except requests.exceptions.ContentDecodingError:
            result = TestResult.CONTENTDECODINGERROR
        except requests.exceptions.ChunkedEncodingError:
            result = TestResult.CHUNKEDENCODINGERROR
        except requests.exceptions.TooManyRedirects:
            result = TestResult.TOOMANYREDIRECTS
        except requests.exceptions.RequestException:
            result = TestResult.REQUESTEXCEPTION
        else:
            http_status_code = resp.status_code

            if http_status_code == 200:
                if urlparse(extlink).scheme == "http":
                    extlink_https = urlparse(extlink)._replace(scheme="https").geturl()

                    try:
                        resp_https = requests.get(extlink_https, headers=HTTP_HEADERS, timeout=5)
                    except requests.exceptions.ConnectTimeout:
                        result = TestResult.NOHTTPS_HTTPS_CONNECTTIMEOUT
                    except requests.exceptions.ReadTimeout:
                        result = TestResult.NOHTTPS_HTTPS_READTIMEOUT
                    except requests.exceptions.ConnectionError:
                        result = TestResult.NOHTTPS_HTTPS_CONNECTIONERROR
                    except requests.exceptions.ContentDecodingError:
                        result = TestResult.NOHTTPS_HTTPS_CONTENTDECODINGERROR
                    except requests.exceptions.ChunkedEncodingError:
                        result = TestResult.NOHTTPS_HTTPS_CHUNKEDENCODINGERROR
                    except requests.exceptions.TooManyRedirects:
                        result = TestResult.NOHTTPS_HTTPS_TOOMANYREDIRECTS
                    except requests.exceptions.RequestException:
                        result = TestResult.NOHTTPS_HTTPS_REQUESTEXCEPTION
                    else:
                        http_status_code = resp_https.status_code

                        if http_status_code == 200:
                            result = TestResult.NOHTTPS_HTTPS_HTTPOK
                        else:
                            result = TestResult.NOHTTPS_HTTPS_HTTPNOK
                else:
                    result = TestResult.HTTPOK
            else:
                result = TestResult.HTTPNOK

        #
        # Handles the request result.
        #

        if result == TestResult.HTTPNOK:
            result_s = f"HTTP {http_status_code}"
        elif result == TestResult.NOHTTPS_HTTPS_HTTPNOK:
            result_s = f"HTTPS available, but \"HTTP {http_status_code}\" when requested"
        else:
            result_s = result.value

        # Stores relevant data.
        # Note: A ConnectionError occurs when HTTPS is not available ;
        #       so, if the link is a valid HTTP link and HTTPS is not available,
        #       there is nothing to fix.
        if result == TestResult.HTTPOK \
        or result == TestResult.NOHTTPS_HTTPS_CONNECTIONERROR:
            print(f"        {'':>{2 * digits_count + 5}}   \033[32m{result_s}\033[39m")
        else:
            print(f"        {'':>{2 * digits_count + 5}}   \033[31m{result_s}\033[39m")

            if result.name.startswith("NOHTTPS_"):
                nohttps_extlinks[extlink] = result_s
            else:
                broken_extlinks[extlink] = result_s

        # Updates the time of the last request to the host of the currently tested link.
        host[2] = request_time

        # Removes the currently tested link from the list of links to be tested.
        del host[1][0]

        #
        # Saves audit results into files.
        # Note: It takes between 0.001 and 0.01 second to do that,
        #       so it's not a problem to do it after each test.
        #

        for extlinks_list, output_file in [(nohttps_extlinks, args.result_nohttps_file),
                                           (broken_extlinks, args.result_broken_file)]:
            if extlinks_list:
                try:
                    f = open(output_file, "w", encoding="utf-8")
                except OSError as e:
                    print(f"        Error while opening \"{output_file}\" : {e.strerror}")
                    sys.exit(1)
                with f:
                    for page in wiki_pages_clean:
                        to_write = ""

                        for link in page[1]:
                            if link in extlinks_list:
                                to_write += f"[{link}] : {extlinks_list[link]}\n\n"

                        if to_write:
                            f.write(f"== [[:{page[0]}]] ==\n\n")
                            f.write(to_write)

        # Checks whether enough time has passed to make
        # another request to the first host tested by this "for" loop.
        # Note: This is needed in order to test as many links
        #       as possible from the first hosts in the list,
        #       since they have the most links to be tested.
        # Note: 110 % (1.1) of the wait time is used in order to
        #       provide a margin, in case some requests during
        #       the next "while" loop finish faster than expected,
        #       which would mess with the wait times of the hosts
        #       following the ones for which the request was "too" fast
        #       (not enough time would have passed since their last requests,
        #       so they would be skipped, which would be inefficient).
        #       A value too small wouldn't have any effect, and
        #       a value too high would greatly increase the duration of
        #       the link testing (especially when less than 4-5 hosts
        #       remains in the list, since this means some time will
        #       inevitably have to be waited at each turn of the loop).
        #       This value seems to work well in practice.
        if time.time() - start_time >= 1.1*args.wait_time:
            break

    # Checks whether the remaining lists of links to be tested are empty.
    if all([not host[1] for host in hosts_sorted]):
        break

    # Removes hosts that don't have external links to be tested anymore.
    hosts_sorted = [host for host in hosts_sorted if host[1]]
    # Sorts the list by decreasing size of links lists.
    # Note: This is needed in case we "break" from the "for" loop,
    #       since some tested hosts' list of links may now have,
    #       after the link testing, one less element than
    #       the following untested host's list of links,
    #       if they initially had the same number of links to be tested.
    # Note: Since sort() is "stable", sorting will not change
    #       the relative order of elements that compare equal.
    #       It means than even if the tested hosts' list of links
    #       and the following untested host's list of links have the same length,
    #       sort() will not put some tested ones several positions later
    #       in the list than some untested ones, which would otherwise
    #       make us uselessly wait some time for tested ones
    #       that we wouldn't actually reach on the next "for" loop.
    hosts_sorted.sort(key=lambda host: len(host[1]), reverse=True)

    #
    # Ensures enough time has passed
    # before the next request to the first host tested.
    #

    # Note: If only one host remains with links to be tested,
    #       there is no more need to provide a margin
    #       for the wait time.
    if len(hosts_sorted) == 1:
        wait_time = args.wait_time
    else:
        wait_time = 1.1*args.wait_time

    delay = time.time() - start_time

    if delay < wait_time:
        sleep_time = wait_time - delay
        sleep_time_floored = math.floor(sleep_time)

        print(f"        Waiting {round(sleep_time, 1)} seconds before the next requests ", end="", flush=True)
        time.sleep(sleep_time - sleep_time_floored)
        print(".", end="", flush=True)
        for i in range(sleep_time_floored):
            time.sleep(1)
            print(".", end="", flush=True)
        print("\n", end="", flush=True)

#
# Displays results summary.
#

count_broken_extlinks = 0
count_nohttps_extlinks = 0

for page in wiki_pages_clean:
    for link in page[1]:
        if link in nohttps_extlinks:
            count_nohttps_extlinks += 1
        if link in broken_extlinks:
            count_broken_extlinks += 1

print()
print("----- Results:")
print(f"        {count_broken_extlinks} broken HTTP(S) external links.")
print(f"        {count_nohttps_extlinks} valid HTTP external links that (may) have an HTTPS version.")
