SBIN - secure paste bin service
===============================

What is sbin?
-------------

BIN.SO is minimalistic paste bin service focused on security:

* Search engines are not allowed to crawl and index content of bin.so
* Uploaded content is assigned with uniq random URL
* Uploaded content is protected by password. Data is encrypted in the browser, then already encrypted data sends to the server.
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


How to run app locally
----------------------

* Clone repo
* Run: make build
* Run: source .env/bin/activate
* Run: python web.py


Migration from 0.0.1 version
----------------------------

Version 0.0.2 uses file system as dumps storage. To move dumps from old database to
new storage run the command: python convert_database.py. It will not destroy old
database, just copy dumps into file system storage. New dumps created with the app
will be stored only to file system storage.


SBIN app live examples
----------------------

* http://bin.so - official instance running by author of sbin
