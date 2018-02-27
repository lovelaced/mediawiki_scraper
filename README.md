# mediawiki_scraper

This script scrapes all categorical data from practicalplants.org into a locally running mongoDB instance.

It requires mwparserfromhell, pymediawiki and the official python mongo module.

This ships with a MODIFIED version of pymediawiki as practicalplants.org uses a very slightly modified version of current mediawiki standards.

The mongoDB instance should be running like this:

`sudo docker run --rm --name my-mongo -it -p 27017:27017 mongo:latest`

To export the database to a JSON file within the docker container, do this:

`sudo docker exec -it my-mongo mongoexport --db database --collection crops --out crop_db.json`
