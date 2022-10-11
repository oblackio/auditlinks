README
======

_From an idea of Ris._

Usage
-----

```
usage: auditlinks.py [-h] [--from-dump-file FILE] [--wait-time DELAY]
                     [--dump-file FILE] [--result-nohttps-file FILE]
                     [--result-broken-file FILE]

Audits HTTP(S) external links from english pages in the "(Main)" namespace of
the Gentoo wiki, and saves results into files (see "Filenames options").

General options:
  -h, --help            Shows this help message and exits.
  --from-dump-file FILE
                        Uses FILE as the source of data for the links to be
                        tested, instead of the [MediaWiki Action API](https://www.mediawiki.org/wiki/API:Main_page).
  --wait-time DELAY     The wait time in seconds between network requests on
                        the same host. (default: 10)

Filenames options:
  --dump-file FILE      The JSON-formatted dump file in which will be saved
                        the list of links to be tested. (default: "dump.json")
  --result-nohttps-file FILE
                        The MediaWiki-formatted result file in which will be
                        saved the list of valid HTTP external links that (may)
                        have an HTTPS version. (default:
                        "result_nohttps.mediawiki")
  --result-broken-file FILE
                        The MediaWiki-formatted result file in which will be
                        saved the list of broken HTTP(S) external links.
                        (default: "result_broken.mediawiki")
```

Practical information
---------------------
_(what follows was correct the 05/10/2022)_

Fetching the list of links takes 69 requests to the MediaWiki Action API, which are done in around 12 minutes _(with the default wait time of 10 seconds between requests to the same host)_.

There are 16662 HTTP(S) external links. 22 % are duplicates.  
There are 13034 unique HTTP(S) external links.  
The dump file for them is 1.2 MiB.

Testing the links takes around 16 hours _(with the default wait time of 10 seconds between requests to the same host)_.

There are 1374 broken HTTP(S) external links.  
The result file for them is 118.9 KiB.  
There are 1390 valid HTTP external links that (may) have an HTTPS version.  
The result file for them is 111.4 KiB.

Link testing algorithm
----------------------

The simplest way to do it is to take one page, test each external link of this page, waiting some time between requests to the same host, then take another page, and repeat.  
And possibly, cache results so that duplicates won't trigger a new request for external links we already tested.

The problem with this approach is that the wait time between requests to the same host will greatly slow down the whole process.  
Often, a page will have a few successive external links to the same host, which will trigger an almost entire wait time.  
It's highly inefficient as the script could check externals links to other hosts during that time, instead of just waiting.

Thus, this script doesn't do that.

The external links are grouped by hosts, and the list of hosts' list of links is sorted by decreasing list length.  
Also, duplicates are removed.  
The script then takes the first host in the list (the one with the most links to be tested), tests a link, then takes the next host, and repeats, until enough time has passed for the script to make a new request to a link from the first host's list of links.  
The list of hosts' list of links is also re-sorted when needed.  
The main idea is to request links from the first hosts in the list as frequently as possible, as this reduces the time the script is waiting as much as possible. 

Why does it take so long ?
--------------------------

It's because of the extreme difference between the hosts' count of links, and of the wait time between requests to the same host.

If links were equally split between all the hosts, the execution time would be minimal : almost no time would be waited.  
In theory, assuming each test takes 1.5 seconds (almost exclusively used by the request), 2400 links could be tested each hour.

However, that is not the case in practice.  
This means that after some time, less than 4-5 hosts remains in the list, and some time will inevitably have to be waited between requests, since the script ran out of other hosts for which it can test links.

As an example, the 15/09/2022, after running for around 2 hours, only 3 hosts remained: gentoo.org, github.com, wikipedia.org.  
After around 2 additional hours, only 1 host remained: gentoo.org.  
This is explained by the fact that, of the 12968 unique external links to be tested: 5503 were from gentoo.org, 1163 were from github.com, 672 were from wikipedia.org. 

Usage with other MediaWiki wikis
--------------------------------

It should be very easy to use it with (or extend it for) other MediaWiki wikis : simply set the value of the variable `API_ENDPOINT` to the API endpoint of the targeted wiki.

The script will work as it is if the following requirements are met:
- the MediaWiki version of the targeted wiki is not too far from the one used by the Gentoo wiki (the 05/10/2022: version 1.35.7)
- the targeted wiki pages don't have translations, or they have translations that follow the same naming as in the Gentoo wiki (<english page URL>/<language code> ; ex: https://wiki.gentoo.org/wiki/FAQ/fr)

Otherwise:
- some MediaWiki API modules that are necessary for the requests may not be available
- some MediaWiki API modules that are necessary for the requests may behave differently
- links from translated pages will be taken into account instead of being skipped

Here are some test results.

| Wiki | API endpoint | Works ? |
| --- | --- |--- |
| [Minetest wiki](https://wiki.minetest.net/Main_Page) | https://wiki.minetest.net/api.php | Yes |
| [Archlinux wiki](https://wiki.archlinux.org/title/Main_page) | https://wiki.archlinux.org/api.php | Yes.<br>However, the translated pages are named differently than in the Gentoo wiki, so the script couldn't skip them. |
| [Git wiki](https://git.wiki.kernel.org/index.php/Main_Page) | https://git.wiki.kernel.org/api.php | No<br />(because of its old MediaWiki version: 1.19.24)<br>However, the script would only need small modifications, since the only differences are that, in the JSON data sent by the Git wiki API, pages are elements of a JSON object (instead of a JSON array), and each external link is the value of an attribute named `*` (instead of `url`). |
