import os
import unittest
import tempfile
import uuid
import base64
import json
import mock
from bunch import Bunch
from schmoxy import util, doc_processor, app

class UtilTests(unittest.TestCase):

    def test_bi_dict(self):
        bi_dict = util.BiDict()
        bi_dict[0] = 'something'
        self.failUnlessEqual(bi_dict[0], 'something')
        self.failUnlessEqual(bi_dict['something'], 0)

img_src_doc = """
<html><body>
Blah blah etc
<img src="%(src)s" />
</body></html>
"""

class DocProcessorTests(unittest.TestCase):

    def test_img_src_relative(self):
        doc = img_src_doc % dict(src="/blah/yada.jpg")
        urls = util.BiDict()
        new_doc = doc_processor.replace_references(doc, "http://example.com",
                                                   urls, "http://new.com")
        self.failUnless('src="http://new.com/blah/yada.jpg"' in new_doc)
        self.failUnlessEqual(urls['http://example.com/blah/yada.jpg'],
                             'http://new.com/blah/yada.jpg')
        self.failUnlessEqual(urls['http://new.com/blah/yada.jpg'],
                             'http://example.com/blah/yada.jpg')


    def test_img_src_absolute(self):
        doc = img_src_doc % dict(src="http://otherpage.net/blah/yada.jpg")
        urls = util.BiDict()
        new_doc = doc_processor.replace_references(doc, "http://example.com",
                                                   urls, "http://new.com")
        self.failUnless('src="http://new.com/blah/yada.jpg"' in new_doc)
        self.failUnlessEqual(urls['http://otherpage.net/blah/yada.jpg'],
                             'http://new.com/blah/yada.jpg')
        self.failUnlessEqual(urls['http://new.com/blah/yada.jpg'],
                             'http://otherpage.net/blah/yada.jpg')

class ResourceCacheTests(unittest.TestCase):

    def setUp(self):
        self.cache_dir = tempfile.mkdtemp()
        self.resource_cache = app.ResourceCache(self.cache_dir, '','')

    @mock.patch('requests.get')
    def test_new_file_cached_returned(self, mock_get):
        mock_response =  Bunch(text=str(uuid.uuid4()),
                               headers={'content-type':'text/html',
                                        'arbitrary-key':'value'})
        url = 'http://example.com'
        mock_get.return_value = mock_response
        headers,content = self.resource_cache.get_resource(url)

        self.failUnless(mock_get.called_once_with(url))
        self.failUnlessEqual(content, mock_response.text)
        filename = base64.b64encode(url, '+_')
        filepath = os.path.join(self.cache_dir, filename)
        self.failUnless(os.path.exists(filepath))
        with open(filepath, 'r') as cache_file:
            self.failUnless(cache_file.read().endswith(mock_response.text))

        self.failUnlessEqual(headers['content-type'], 'text/html')
        self.failUnlessEqual(headers['arbitrary-key'], 'value')


    def test_cache_returned_if_exists(self):
        url = 'http://blah.com'
        encoded = base64.b64encode(url, '+_')
        text = str(uuid.uuid4())
        headers = json.dumps(dict(yada='etc'))
        with open(os.path.join(self.cache_dir, encoded), 'w') as outfile:
            outfile.write("%d%s" % (len(headers), headers))
            outfile.write(text)
        headers, content = self.resource_cache.get_resource(url)
        self.failUnlessEqual(content, text)


    @mock.patch('requests.get')
    def test_binary_resource(self, mock_get):
        with open('sample.gif', 'rb') as sample_gif:
            content = sample_gif.read()
        headers = {'content-length': '3305', 'content-type': 'image/gif'}
        mock_response = Bunch(content=content, headers=headers)
        mock_get.return_value = mock_response

        return_headers, content = self.resource_cache.get_resource('http://example.com')
        self.failUnlessEqual(content, content)
        self.failUnlessEqual(headers, return_headers)



if __name__ == "__main__":
    unittest.main()
