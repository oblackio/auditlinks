TODO
====

- resume a previously interrupted audit session
  - resume fetching data from MediaWiki Action API when there was an interruption  
  **--> Idea:** For each request, just store in a file the previous + current request's URL parameters.
  - resume testing external links when there was an interruption

- automatically make edits on the wiki to fix the valid HTTP external links that have an HTTPS version

- parallelize requests  
**--> Idea:** Use several processes, and evenly affect to each of them a separate set of hosts.  
**--> Note:** This would actually not be very useful, as there is a large difference between the hosts' count of links (see README).

- test other URI schemes
  - `git://`
  - `irc://`, `ircs//`
  - `mailto:`  
  **--> Idea :** https://stackoverflow.com/questions/53561296/python-correct-method-verify-if-email-exists
