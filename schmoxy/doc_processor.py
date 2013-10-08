from urlparse import urlparse, urljoin, ParseResult
from BeautifulSoup import BeautifulSoup

def replace_references(page_text, source_url, urls_dict, server_name):
    soup = BeautifulSoup(page_text)
    for img in soup.findAll('img'):
        src = urlparse(img['src'])
        if not src.netloc:
            #we want the absolut url so that it can be downloaded later
            src = urlparse(urljoin(source_url, img['src']))
        try:
            new_src = urls_dict[src.geturl()]
        except KeyError:
            scheme = ('http' if '//' not in server_name
                      else server_name.split('//')[0][:-1])
            server_name = (server_name.split('//')[1] if '//' in server_name
                           else server_name)
            new_src = ParseResult(scheme,
                                  server_name,
                                  src.path, src.params, src.query, src.fragment).geturl()
            urls_dict[src.geturl()] = new_src
        img['src'] = new_src
    return unicode(soup)
