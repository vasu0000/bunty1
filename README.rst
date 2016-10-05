SBIN - secure paste bin service
===============================

What is sbin?
-------------

BIN.SO is minimalistic paste bin service focused on security:

* Search engines are not allowed to crawl and index content uploaded to application
* Each uploaded content is assigned with uniq random ID
* Uploaded content could be protected by password. Data is encrypted in the browser, then *encrypted* data sends to the server.

What happens if I protect content with password?
------------------------------------------------

First, data is encrypted on client-side, just inside browser. Then data is submitted to the
server. Server stores already encrypted data, it is not possible to read data even you have direct
access to the database.

When you open content's page the encrypted data is loaded from the server to web-browser. Then you 
provide the password and it is used to decrypt data and display it in the browser.
