# API

The ToC file is parsed to a `SiteMap`, which is a `MutableMapping` subclass, with keys representing docnames mapping to a `Document` that stores information on the toctrees it should contain:

```python
import yaml
from sphinx_external_toc.parsing import parse_toc_yaml
path = "path/to/_toc.yml"
site_map = parse_toc_yaml(path)
yaml.dump(site_map.as_json())
```

Would produce e.g.

```yaml
root: intro
documents:
  doc1:
    docname: doc1
    subtrees: []
    title: null
  intro:
    docname: intro
    subtrees:
    - caption: Subtree Caption
      numbered: true
      reversed: false
      items:
      - doc1
      titlesonly: true
    title: null
meta: {}
```
