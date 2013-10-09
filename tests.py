import os
import unittest
import tempfile
import uuid
import base64

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

class GetResourceTests(unittest.TestCase):

    def setUp(self):
        self.cache_dir = tempfile.mkdtemp()

    @mock.patch('requests.get')
    def test_new_file_cached_returned(self, mock_get):
        mock_response =  Bunch(text=str(uuid.uuid4()),
                               headers={'content-type':'text/html'})
        url = 'http://example.com'
        mock_get.return_value = mock_response
        return_val = app.get_resource(self.cache_dir, url)
        self.failUnless(mock_get.called_once_with(url))
        self.failUnlessEqual(return_val, mock_response.text)
        filename = base64.b64encode(url, '+_')
        filepath = os.path.join(self.cache_dir, filename)
        self.failUnless(os.path.exists(filepath))
        with open(filepath, 'r') as cache_file:
            self.failUnlessEqual(cache_file.read(), mock_response.text)


    def test_cache_returned_if_exists(self):
        url = 'http://blah.com'
        encoded = base64.b64encode(url, '+_')
        text = str(uuid.uuid4())
        with open(os.path.join(self.cache_dir, encoded), 'w') as outfile:
            outfile.write(text)
        self.failUnlessEqual(app.get_resource(self.cache_dir, url), text)


if __name__ == "__main__":
    unittest.main()
