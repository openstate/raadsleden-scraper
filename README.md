# Raadsleden Scraper
This repository contains code for a tool that can automatically find and scrape data about political representatives with sitemaps as an input.

## Purpose
Maintaining web scrapers is a time consuming task, layouts may change or data may be placed elsewhere on the site.
It would be very convenient if a scraper could find the data we want automatically, without having to specify on which page and where on the page the data is presented.
With this tool we attempt to extract data about political representatives from a large number of Dutch municipality websites.

We currently have the following file structure:
- fetch_members.py -> Main controller script, also extracts data from sites who make use of detail pages to describe one person
- sitemap_url_pattern_finder.py -> Finds url patterns in a given sitemap, to find detail pages
- fetch_members_one_page.py -> Extracts data from a page which should include data about more than one person.
- open_result_file.py -> Example script on how to extract the data from the result json file
 
## Important links
 - [Almanak datasets](https://almanak.overheid.nl/archive/) to extract the websites of municipalities
 - [Official source code repo](https://github.com/openstate/raadsleden-scraper/)

## Install and usage
 - Add the sitemaps of the targeted websites to the directory '/sitemaps/extracted/'
    -  We have used the tool [python-sitemap](https://github.com/Bash-/python-sitemap) with a rate limiter to build sitemaps
 - Optional: configure the keywords for pattern recognition in 'sitemap_url_pattern_finder.py' 
 - Run fetch_members.py for starting the matching algorithms
 - The '/pickles/files/' directory contains the result files per municipality

## Author

Bas Hendrikse ([@bas_hendrikse](https://twitter.com/bas_hendrikse))

## Copyright and license

The Raadsleden Scraper is licensed under CC0.
