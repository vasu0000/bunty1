SBIN - secure paste bin service
===============================

What is sbin?
-------------

BIN.SO is minimalistic paste bin service focused on security:

* Search engines are not allowed to crawl and index content of bin.so
* Uploaded content is assigned with uniq random URL
* Uploaded content is protected by password. Data is encrypted in the browser, then
    already encrypted data sends to the server.
* You can't read data even if you hack the server and read database directly

Quickiest way to go live on heroku in few clicks
------------------------------------------------

* Fork github repo
* Create new application in heroku dashboard
* On Deply tab choose Github option and connect forked repo
* Click "Deploy Branch" in Manual deploy section
* Wait 30 seconds
* Click "View" button
* PROFIT!!!

SBIN app live examples
----------------------

* http://bin.so - official instance running by author of sbin
