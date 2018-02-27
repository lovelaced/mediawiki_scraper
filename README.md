# mediawiki_scraper

This script scrapes all categorical data from practicalplants.org into a locally running mongoDB instance.

It requires mwparserfromhell, pymediawiki (LATEST VERSION ONLY) and pymongo. You can use beautifulsoup as well for extra debugging info.

The mongoDB instance should be running like this:

`sudo docker run --rm --name my-mongo -it -p 27017:27017 mongo:latest`

To export the database to a JSON file within the docker container, do this:

`sudo docker exec -it my-mongo mongoexport --db database --collection crops --out crop_db.json`

To copy the file from the docker container to a local directory, do this:

`sudo docker cp <CONTAINER_ID>:/crop_db.json /path/to/localdir`
