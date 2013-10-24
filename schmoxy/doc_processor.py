import re
from bs4 import BeautifulSoup
from furl import furl


def local_to_remote(src, origin, server_name, urls_dict):
    if not src.scheme:
        src.scheme = origin.scheme
    if not src.netloc:
        src.netloc = origin.netloc
    try:
        new_src = urls_dict[src.url]
    except KeyError:
        new_src = src.copy()
        new_src.scheme = 'http'
        new_src.netloc = server_name.netloc
        urls_dict[src.url] = new_src.url
    return new_src


def regexp_matches_js(script_node, js_regexp):
    if script_node.has_attr('src'):
        return bool(re.search(js_regexp, script_node['src']))
    return bool(re.search(js_regexp, script_node.text))


def replace_references(page_text, source_url, urls_dict, server_name, excluded_js=None):
    source_url = furl(source_url)
    server_name = (furl(server_name) if server_name.startswith('http://')
                   else furl('http://' + server_name))

    soup = BeautifulSoup(page_text)
    for img in soup.find_all('img'):
        img['src'] = local_to_remote(furl(img['src']), source_url,
                                     server_name, urls_dict)
    for css in [x for x in soup.find_all('link') if x['rel'] == ['stylesheet']]:
        css['href'] = local_to_remote(furl(css['href']), source_url,
                                      server_name, urls_dict)
    for script in soup.find_all('script'):
        if excluded_js and  any(regexp_matches_js(script, regexp)
                                for regexp in excluded_js):
            script.extract()

    for script in [x for x in soup.find_all('script') if x.has_attr('src')]:
        script['src'] = local_to_remote(furl(script['src']), source_url,
                                        server_name, urls_dict)
    return unicode(soup)
