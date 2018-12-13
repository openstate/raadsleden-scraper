
'''
TODO:
- Load XML
- Search for string that might be contained in an URL which defines the Gemeenteraadsleden page
- Curl / Fetch content of the potential URL
- Look for information, like Twitter / FB link / telephone number / name / party
- If multiple pages with same tags, but different information, log the urls with their information into a dataframe, save to file
- If the page contains multiple names and social media links, parties etc. first save page to file, later extract data to dataframe
- Manually check if automatically found information is correct. Optimize and go to next xml
'''
class SitemapUrlPatternFinder():
    from lxml import etree
    from difflib import SequenceMatcher
    import copy

    tags = [
        'gemeenteraad',
        'Gemeenteraad',
        'samenstelling',
        'mensen',
        'raadsl',
        'bestuur',
        'Bestuur'
    ]
    #

    excluded = [
        'steun',
        'nieuws'
    ]

    def __init__(self):
        print("init")
        import sys
        sys.setrecursionlimit(10000)
        # potentials = self.findPotentials()
        # patterns = self.findPattern(potentials)
        # ptnl_member_pgs = self.findTopLevelUrlPath(patterns, potentials)
        # print(ptnl_member_pgs)

    def findPatternByDomain(self, siteMapUrl):
        potentials = self.findPotentials(siteMapUrl)
        patterns = self.findPattern(potentials)
        ptnl_member_pgs = self.findTopLevelUrlPath(patterns, potentials)
        return ptnl_member_pgs

    def findPotentials(self, siteMapUrl):
        parser = self.etree.XMLParser(ns_clean=True)
        xmlContent = self.etree.parse(siteMapUrl, parser)
        links = xmlContent.xpath('//s:loc/text()', namespaces={'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
        links = [link.strip() for link in links]

        potentials = []
        for link in links:
            if any(x in link for x in self.tags) and not any(x in link for x in self.excluded):
                potentials.append(link)
        return potentials

    def findPattern(self, potentials):
        pattern_set = set()
        clone = self.copy.deepcopy(potentials)
        for potential in potentials:
            for index, potential2 in enumerate(clone):
                if potential != potential2:
                    sqm = self.SequenceMatcher(None, potential, potential2)
                    matching_blocks = sqm.get_matching_blocks()
                    for mb in matching_blocks:
                        # if mb.size > 8 and "://" in potential[mb.a: mb.a + mb.size] and len(potential[mb.a: mb.a + mb.size].split('/')) > 3 and potential[mb.a: mb.a + mb.size].split('/')[-1] != "":
                        #     pattern_set.add(potential[mb.a: mb.a + mb.size])

                        if mb.size > 8 and "://" in potential[mb.a: mb.a + mb.size] and len(potential[mb.a: mb.a + mb.size].split('/')) > 4 and potential[mb.a: mb.a + mb.size].split('/')[-1] != "":
                            pattern = "/".join(potential[mb.a: mb.a + mb.size].split('/')[:-1]) + "/"
                            pattern_set.add(pattern)
        return pattern_set

    def findPattern2(self, potentials):
        pattern_set = set()
        clone = self.copy.deepcopy(potentials)
        for potential in potentials:
            for index, potential2 in enumerate(clone):
                if potential != potential2:
                    sqm = self.SequenceMatcher(None, potential, potential2)
                    matching_blocks = sqm.get_matching_blocks()
                    for mb in matching_blocks:
                        if mb.size > 8 and "://" in potential[mb.a: mb.a + mb.size]:
                            pattern_set.add(potential[mb.a: mb.a + mb.size])

                        # if mb.size > 8:
                        #     pattern = "/".join(potential[mb.a: mb.a + mb.size].split('/')[:-1]) + "/"
                        #     pattern_set.add(pattern)
        return pattern_set

    def findTopLevelUrlPath(self, patterns, potentials):
        ptnl_member_ptrn = []
        for pattern in patterns:
            count = 0
            for potential in potentials:
                if pattern in potential:
                    count += 1
            if count > 8:
                ptnl_member_ptrn.append(pattern)
        # self.find_landing_page(patterns, potentials)

        topLevel = []
        for ptnl_ptrn in ptnl_member_ptrn:
            found = False
            for ptnl_ptrn2 in ptnl_member_ptrn:
                if ptnl_ptrn != ptnl_ptrn2 and ptnl_ptrn in ptnl_ptrn2:
                    found = True
            if not found:
                topLevel.append(ptnl_ptrn)
        # return topLevel
        return ptnl_member_ptrn

    # def find_landing_page(self, patterns, potentials):
    #     from urllib.request import urlopen
    #     potential_landing_page = []
    #     print("potentials")
    #     print(potentials)
    #
    #     print("patterns")
    #     print(patterns)

        # for url in patterns:
        #     # print()
        #     # print(url)
        #     html = urlopen(url)
        #     soup = BeautifulSoup(html, 'lxml')
        #     hrefs = soup.body.findAll('a', href=True)
        #     # print(hrefs)
        #     count = 0
        #     link_potentials = []
        #     for link in hrefs:
        #         # print(link)
        #         found = False
        #         for pot in potentials:
        #             if not found and link.get('href') in pot:
        #                 count += 1
        #                 found = True
        #                 link_potentials.append(link.get('href'))
        #     link_patterns = self.findPattern2(link_potentials)
        #     # link_patterns = []
        #     # if count > 9 and len(link_patterns) > 0:
        #     #     potential_landing_page.append({'url': url, 'count': count, "link_patterns": link_patterns})
        #
        #     for link in link_patterns:
        #         link_count = 0
        #         for h in hrefs:
        #             if link in h.get('href'):
        #                 link_count += 1
        #         if link_count > 4 and len(link) > 2:
        #             potential_landing_page.append({'url': link, 'count': link_count})
        #
        # print("POTENTIAL LANDING PAGE")
        # print(potential_landing_page)
        # print(max(potential_landing_page, key=lambda d: d['count']))

if __name__ == "__main__":
    SitemapUrlPatternFinder()
