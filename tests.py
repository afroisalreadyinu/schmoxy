import unittest

from schmoxy import util, doc_processor

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



if __name__ == "__main__":
    unittest.main()
