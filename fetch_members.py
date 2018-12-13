'''
TODO:
- Load Almanak XML
- Search for string that might be contained in an URL which defines the Gemeenteraadsleden page
- Curl / Fetch content of the potential URL
- Look for information, like Twitter / FB link / telephone number / name / party
- If multiple pages with same tags, but different information, log the urls with their information into a dataframe, save to file
- If the page contains multiple names and social media links, parties etc. first save page to file
- Manually check if automatically found information is correct
'''

#TODO op een pagina checken of er veel zelfde patronen staan, dus [gemeente].nl/[naam]/ om dit level ook te herkennen, nu is alleen vanaf [gemeente].nl/*/[naam]/

import pandas as pd
import json
import glob
import unidecode
import fetch_members_one_page
from ratelimit import limits, sleep_and_retry

class FetchMembers:
    from lxml import etree
    import re
    from bs4 import BeautifulSoup
    from sitemap_url_pattern_finder import SitemapUrlPatternFinder

    import pandas as pd

    sitemapUrl = './sitemaps/westland.xml'
    sitemapUrls = ['./sitemaps/sitemap_00620.xml']
    sitemapUrls = ['./sitemaps/extracted/sitemap_00766.xml'] # Dongen, alleen images op de detail paginas
    sitemapUrls = ['./sitemaps/extracted/sitemap_00576.xml']
    sitemapUrls = ['./sitemaps/extracted/sitemap_00119.xml'] # Meppel
    sitemapUrls = ['./sitemaps/extracted/sitemap_00373.xml']
    sitemapUrls = ['./sitemaps/extracted/sitemap_00383.xml']  # Castricum, een pagina met containers per partij
    sitemapUrls = [
        './sitemaps/extracted/sitemap_01903.xml']  # eijsden-margraten een pagina alles, maar vindt een patroon
    sitemapUrls = glob.glob("./sitemaps/extracted/sitemap_*.xml")

    tags = [
    ]

    def __init__(self):
        print("init")
        print()
        # g = glob.glob("./sitemaps/extracted/sitemap_*.xml")

        # self.findUrlPath(self.sitemapUrl)
        already_extracted = [self.re.findall("\d+", sitemap)[0] for sitemap in glob.glob("./pickles/files/sitemap_*.json")]
        sitemap_urls = [url for url in self.sitemapUrls if self.re.findall("\d+", url)[0] not in already_extracted]
        self.crawl(sitemap_urls)
        # pp.pprint(self.crawl(self.sitemapUrls))

        # print("empty, email, phone, twitter, linkedin, instagram, total")
        # for data in self.open_df_from_file("./pickles/sitemap_00620.json"):
        #     print(data.get('url'))
        #     self.get_df_score(pd.read_json(data.get('df')))
        # pp.pprint(self.find_best_page(self.open_df_from_file("./pickles/sitemap_00620.json")))

        # df = self.find_best_page(self.open_df_from_file("./pickles/sitemap_00620.json")).get('df')
        # print("asdfas")
        # print(df)
        # df_new = self.pd.read_json(df)
        # df_new.to_csv("./pickles/results_00620.csv")

        # pp.pprint(self.fetch_url("https://www.velsen.nl/bestuur-organisatie/gemeenteraad/samenstelling-gemeenteraad/velsen-lokaal/mgje-marianne-vos-vester"))
        # pp.pprint(self.getFieldsFromPage(["https://www.velsen.nl/bestuur-organisatie/gemeenteraad/samenstelling-gemeenteraad/velsen-lokaal/mgje-marianne-vos-vester"]).to_csv())

        # self.write_file(self.crawl(self.sitemapUrls))
        # self.write_file(self.crawl([g[6]]))
        # pp.pprint(self.crawl([g[0]]))

        # import requests
        # html = requests.get('https://www.aalsmeer.nl/bestuur-organisatie/bestuurder/dirk-van-willegen').text
        # soup = self.BeautifulSoup(html, 'lxml')
        # self.get_fields(soup, 'https://www.aalsmeer.nl/bestuur-organisatie/bestuurder/')

    def write_file(self, mapping):
        """
        Write the given mapping to a file
        :param mapping: List
        """
        f = open('./pickles/web_extracted.json', 'w')
        f.write('{ "mapping": [')
        for index, item in enumerate(mapping):
            f.write(json.dumps(item))
            if index != len(mapping)-1:
                f.write(",\n")
        f.write("]}")
        print('done')

    def crawl(self, sitemaps):
        """
        Controller function, tries to find person details, based off the sitemap
        :param sitemaps: List of sitemap file names
        :return: List with data for each sitemap
        """
        data_map = []
        for sitemap in sitemaps:
            data_pattern = self.find_url_path(sitemap)
            ictu = self.re.findall("\d+", sitemap)[0]
            FMOP = fetch_members_one_page.FetchMembersOnePage()
            one_page_data = []
            potentials = self.SitemapUrlPatternFinder().findPotentials(sitemap)
            for index, potential in enumerate(potentials):
                # pp.pprint(FMOP.find_url_path(potential))
                data = {
                    "url": potential,
                    "df": FMOP.find_url_path(potential).to_json()
                }
                one_page_data.append(data)

            site_data = data_pattern + one_page_data

            with open("./pickles/files/sitemap_" + ictu + ".json", 'w') as outfile:
                outfile.write('{ "mapping": [')
                for index, url_data in enumerate(site_data):
                    outfile.write(json.dumps(url_data))
                    if index != len(url_data) - 1:
                        outfile.write(",\n")
                outfile.write("]}")
                outfile.close()
            print("Done writing file " + "./pickles/files/sitemap_" + ictu + ".json")
            best_page = self.find_best_page(site_data)
            data_map.append({"url": sitemap, "data": best_page, "id": ictu})

        return data_map

    def get_sitemap_urls(self, sitemap_url):
        """
        :param sitemap_url: Path and filename of a sitemap
        :return: List with all sitemap urls in the sitemap
        """
        parser = self.etree.XMLParser(ns_clean=True)
        xmlContent = self.etree.parse(sitemap_url, parser)
        links = xmlContent.xpath('//s:loc/text()', namespaces={'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
        links = [link.strip() for link in links]
        return links

    def retrieve_sitemap_urls(self, top_level_url, sitemap_url):
        """
        :param top_level_url: An url which should be present as a substring of more urls
        :param sitemap_url: The path and filename of a sitemap
        :return: All urls which contain the top_level_url as a substring
        """
        subLinks = [link for link in self.get_sitemap_urls(sitemap_url) if top_level_url in link]
        return subLinks

    @sleep_and_retry
    @limits(calls=1, period=5)
    def fetch_url(self, url):
        """
        :param url: Webpage url
        :return: Extracted field values on the page
        """
        import requests

        headers = {'user-agent': 'User-Agent: Mozilla/5.0 (compatible; OpenStateBot/1.0; +https://openstate.eu/bot)'}
        req = requests.get(url, headers=headers)
        res = None
        if 'application/pdf' not in requests.get(url).headers.get('content-type'):
            soup = self.BeautifulSoup(req.text, 'lxml')
            res = self.get_fields(soup, url)
        return res

    def get_fields(self, soup, url):
        """
        Extract data from a Beautiful soup document with the use of regex
        :param soup: Container which should contain fields
        :param url: Url of the page that was loaded into a soup
        :return: Dict with all specified fields on the page
        """
        phonenrs = soup.findAll(text=self.re.compile('[0-9- ()+]{10,16}$'))
        # pnrs = [self.re.sub('\D', "", phonenr) for phonenr in phonenrs]

        emailaddrs_href = soup.findAll(href=self.re.compile('\S+@{1}\S+\.'))
        emailaddrs_text = soup.findAll(text=self.re.compile('\S+@{1}\S+\.'))
        emailaddrs = []
        if len(emailaddrs_text) > 0 or len(emailaddrs_href) > 0:
            emailaddrs = emailaddrs_text if len(emailaddrs_text) > len(emailaddrs_href) else [eh['href'] for eh in emailaddrs_href]

        twitterlink = soup.findAll(href=self.re.compile('twitter\.com'))
        twitterlinks = [tl.get('href') for tl in twitterlink]

        linkedlink = soup.findAll(href=self.re.compile('linkedin\.com'))
        linkedlinks = [ll.get('href') for ll in linkedlink]

        instagramlink = soup.findAll(href=self.re.compile('instagram\.com'))
        instagramlinks = [ll.get('href') for ll in instagramlink]

        homeaddress = soup.findAll(text=self.re.compile('[A-z]+\W(\d){1,5}\w*(?:$|\n)'))
        homeaddresses = [unidecode.unidecode(ha.strip()) for ha in homeaddress]
        postalcode = soup.findAll(text=self.re.compile('\d{4}\s?[A-z]{2}(?:$|\n|(\s+[A-z]+))'))
        postalcodes = [unidecode.unidecode(pc.strip()) for pc in postalcode]

        imagelinks = soup.findAll('img')
        imagelinks = [img for img in imagelinks if img.get('src') and "analytics" not in img.get('src')]
        for index, imglink in enumerate(imagelinks):
            if imglink.get('src'):
                if "://" not in imglink['src']:
                    if imglink['src'].startswith("./"):
                        imglink['src'] = imglink['src'][1:]  # remove the dot
                    imagelinks[index] = url.split(".nl")[0] + ".nl" + imglink['src']
                else:
                    imagelinks[index] = imglink['src']

        return {
            'telephone': phonenrs,
            'email': emailaddrs,
            'twitter': twitterlinks,
            'linkedin': linkedlinks,
            'instagram': instagramlinks,
            'image': imagelinks,
            'homeaddress': homeaddresses,
            'postalcode': postalcodes,
            'full_soup': soup
        }

    def get_fields_from_page(self, urls):
        """
        After having fetched the fields from all urls, combine the dicts and keep fields that are
         page specific (no duplicates across pages)
        :param urls: Urls that need to be fetched
        :return: Pandas DataFrame with the data for the given urls
        """
        raadslid_fields = []
        for url in urls:
            raadslid_fields.append(self.fetch_url(url))

        df_dict = {}
        # only add fields (email, twitter, etc.) that are page specific (no duplicates across pages in path)
        for key in raadslid_fields[0].keys():
            non_flat = [rlid.get(key) for rlid in raadslid_fields]
            all_key_values = [value for value2 in non_flat for value in value2]
            duplicates = set([value for value in all_key_values if all_key_values.count(value) > 1])  #TODO This (count > 1) results in no images if the image is reused across pages
            df_dict[key] = [[x for x in lst if x not in duplicates] for lst in non_flat]

        df = self.pd.DataFrame(df_dict)
        return df

    def find_url_path(self, sitemap_url):
        """
        First find patterns of urls in the sitemap then construct a DataFrame per pattern and determine which contains the best data
        :param sitemap_url: The path and filename to the sitemap
        :return: The top-level url with its data, which is constructed from the fields on the pages which have the given url as a substring of its page url
        """
        site_map_obj = self.SitemapUrlPatternFinder()
        top_level = site_map_obj.findPatternByDomain(sitemap_url)
        print(top_level)
        potential_pages = []

        for index, topLevelUrl in enumerate(top_level):
            print(topLevelUrl)
            urls = self.retrieve_sitemap_urls(topLevelUrl, sitemap_url)
            df = self.get_fields_from_page(urls)
            data = {
                "url": topLevelUrl,
                "df": df.to_json()
            }
            potential_pages.append(data)
        return potential_pages

    @staticmethod
    def open_df_from_file(file_name):
        with open(file_name) as f:
            load = json.load(f)
        return load.get('mapping')

    def find_best_page(self, potential_pages):
        """
        :param potential_pages: Dicts with DataFrame with numerous extracted fields
        :return: The dict that is probably the url which contains the data we are looking for
        """
        best_page = potential_pages[0] if len(potential_pages) > 0 else None
        if len(potential_pages) > 1:
            for page in potential_pages:
                if self.get_df_score(pd.read_json(page.get('df'))) > self.get_df_score(pd.read_json(best_page.get('df'))):
                    best_page = page
        return best_page

    @staticmethod
    def get_df_score(df):
        """
        :param df: DataFrame
        :return: Score based on the number of fields that are filled in the DataFrame
        """
        df_empty = df[df['email'].map(lambda d: len(d)) == 0].shape[0]
        df_email = df[df['email'].map(lambda d: len(d)) > 0].shape[0]
        df_phone = df[df['telephone'].map(lambda d: len(d)) > 0].shape[0]
        df_twitter = df[df['twitter'].map(lambda d: len(d)) > 0].shape[0]
        df_linkedin = df[df['linkedin'].map(lambda d: len(d)) > 0].shape[0]
        df_instagram = df[df['instagram'].map(lambda d: len(d)) > 0].shape[0]
        df_image = df[df['image'].map(lambda d: len(d)) > 0].shape[0]
        return (df_phone + df_twitter + df_linkedin + df_instagram + df_email + df_image) / (df_empty/6 + 1)

if __name__ == "__main__":
    FetchMembers()
