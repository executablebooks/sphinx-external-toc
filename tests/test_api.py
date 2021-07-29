from sphinx_external_toc.api import Document, FileItem, SiteMap, TocTree


def test_sitemap_get_changed_identical():
    """Test for identical sitemaps."""
    root1 = Document("root")
    root1.subtrees = [TocTree([])]
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.subtrees = [TocTree([])]
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == set()


def test_sitemap_get_changed_root():
    """Test for sitemaps with changed root."""
    doc1 = Document("doc1")
    doc2 = Document("doc2")
    sitemap1 = SiteMap(doc1)
    sitemap1["doc2"] = doc2
    sitemap2 = SiteMap(doc2)
    sitemap1["doc1"] = doc1
    assert sitemap1.get_changed(sitemap2) == {"doc1"}


def test_sitemap_get_changed_title():
    """Test for sitemaps with changed title."""
    root1 = Document("root")
    root1.title = "a"
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.title = "b"
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == {"root"}


def test_sitemap_get_changed_subtrees():
    """Test for sitemaps with changed subtrees."""
    root1 = Document("root")
    root1.subtrees = [TocTree([])]
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.subtrees = [TocTree([FileItem("a")])]
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == {"root"}


def test_sitemap_get_changed_subtrees_numbered():
    """Test for sitemaps with changed numbered option."""
    root1 = Document("root")
    root1.subtrees = [TocTree([], numbered=False)]
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.subtrees = [TocTree([], numbered=True)]
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == {"root"}
