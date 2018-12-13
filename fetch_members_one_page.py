import unidecode

class FetchMembersOnePage:
    import re
    import bs4
    from bs4 import BeautifulSoup
    from sitemap_url_pattern_finder import SitemapUrlPatternFinder as spf
    import pandas as pd
    from ratelimit import limits, sleep_and_retry

    siteMapUrl = './sitemaps/putten.xml'

    tags = [
    ]

    def __init__(self):
        print("init")
        # siteMapObj = self.spf()
        # potentials = siteMapObj.findPotentials(self.siteMapUrl)
        # potentials = ["https://www.rheden.nl/gemeenteraad/Gemeente_raad/Over_de_gemeenteraad/Raadsleden"]
        potentials = [
            "https://www.gemeenteberkelland.nl/Gemeenteraad/Gemeenteraad/De_gemeenteraad/Raadsleden_2018_2022"]
        # potentials = ["https://ris.ibabs.eu/raad-ettenleur/raadsleden/"]
        potentials = ["https://www.gemeenteraadzundert.nl/index.php?n1_id=2&n2_id=4"]
        potentials = ["https://www.gemert-bakel.nl/samenstelling-raad"]
        potentials = ["https://www.gemeentesluis.nl/Bestuur_en_Organisatie/Gemeenteraad/Samenstelling"]
        potentials = ["https://www.castricum.nl/raad-en-college/samenstelling-gemeenteraad/"]
        potentials = ["https://www.oostgelre.nl/raadsleden"]
        potentials = ["https://www.pekela.nl/Bestuur/Gemeenteraad/Raadsleden"]
        potentials = ["https://www.putten.nl/Bestuur/Gemeenteraad/Samenstelling_2018_2022"]
        potentials = ["https://www.eijsden-margraten.nl/bestuur/gemeenteraad/samenstelling-gemeenteraad.html"]
        # self.find_url_path(potentials)

    def find_url_path(self, potential):
        return self.get_fields_from_page(potential)

    def get_fields_from_page(self, url):
        # print(url)
        fields = self.fetch_url(url)
        total_fields = [{
            'telephone': [],
            'email': [],
            'twitter': [],
            'linkedin': [],
            'instagram': [],
            'image': [],
            'homeaddress': [],
            'postalcode': [],
            'full_soup': []
        }]
        if fields:
            field_containers = fields.get('email') if len(fields.get('email')) > 6 or \
                                                      len(fields.get('telephone')) < len(fields.get('email')) else fields.get('telephone')
            wrapper_containers = []
            for container in field_containers:
                detail_container = self.find_detail_container(container)
                wrapper_containers.append(detail_container)
                total_fields.append(self.get_fields(detail_container, url))

            # for w in wrapper_containers:
                # print()
                # pp.pprint(w)

            # convert bs4 NavigableString to string
            for field in total_fields:
                field['email'] = [mailfield.string for mailfield in field.get('email')]

            # if container.name == "tbody":
            #     all_container = container.find_parent()
            # print(container)
            # print(self.get_fields(container, url))

            # print(url)
            # for entry in total_fields:
            #     for index, value in enumerate(entry.get('email')):
            #         print(type(value))
            #         if type(value) is self.bs4.element.NavigableString:
            #             print("Entry:")
            #             print(entry)
            #             entry.get('email')[index] = value['href']
            # pp.pprint(total_fields)

        df = self.pd.DataFrame(total_fields)
        return df

    @sleep_and_retry
    @limits(calls=4, period=1)
    def fetch_url(self, url):
        import requests
        headers = {'user-agent': 'User-Agent: Mozilla/5.0 (compatible; OpenStateBot/1.0; +https://openstate.eu/bot)'}
        req = requests.get(url, headers=headers)
        res = None
        if 'application/pdf' not in requests.get(url).headers.get('content-type'):
            soup = self.BeautifulSoup(req.text, 'lxml')
            res = self.get_fields(soup, url)
        return res

    def get_fields(self, soup, url):
        phonenrs = soup.findAll(string=self.re.compile('[0-9- ()+]{10,16}$'))
        # pnrs = [self.re.sub('\D', "", phonenr) for phonenr in phonenrs]

        emailaddrs_href = soup.findAll(href=self.re.compile('\S+@{1}\S+\.'))
        emailaddrs_text = soup.findAll(text=self.re.compile('\S+@{1}\S+\.'))
        emailaddrs = emailaddrs_text if len(emailaddrs_text) > len(emailaddrs_href) else emailaddrs_href

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
        for index, imglink in enumerate(imagelinks):
            if imglink.get('src'):
                if "://" not in imglink.get('src'):
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

    def find_detail_container(self, container):
        res = container
        is_container = self.scan_container_for_field(container)
        while not is_container:
            if not is_container:
                res = container
                container = container.find_parent()
            if not container:
                is_container = True
            else:
                is_container = self.scan_container_for_field(container)
        return res

    def scan_container_for_field(self, container):
        res = False
        if type(container) is self.bs4.element.Tag:
            emailaddrs_href = container.findAll(href=self.re.compile('\S+@{1}\S+\.'))
            emailaddrs_text = container.findAll(text=self.re.compile('\S+@{1}\S+\.'))
            emailaddrs = emailaddrs_text if len(emailaddrs_text) > len(emailaddrs_href) else emailaddrs_href
            res = len(emailaddrs) > 1
        return res

if __name__ == "__main__":
    FetchMembersOnePage()
