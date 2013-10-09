from urlparse import urlparse, urljoin, ParseResult
from BeautifulSoup import BeautifulSoup

def local_to_remote(src, origin, server_name, urls_dict):
    if not urlparse(src).netloc:
        #we want the absolute url so that it can be downloaded later
        src = urlparse(urljoin(origin, src))
    else:
        src = urlparse(src)
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
    return new_src


def replace_references(page_text, source_url, urls_dict, server_name):
    soup = BeautifulSoup(page_text)
    for img in soup.findAll('img'):
        img['src'] = local_to_remote(img['src'], source_url,
                                     server_name, urls_dict)

    for css in [x for x in soup.findAll('link') if x['rel'] == 'stylesheet']:
        css['href'] = local_to_remote(css['href'], source_url,
                                      server_name, urls_dict)

    for script in [x for x in soup.findAll('script') if x.has_key('src')]:
        script['src'] = local_to_remote(script['src'], source_url,
                                        server_name, urls_dict)
    return unicode(soup)
