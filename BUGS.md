# Bugs

```
  File "/code/botify/compat.py", line 15
    from . import utils.slownumbers as fastnumbers
                       ^
SyntaxError: invalid syntax
```

```
  File "/code/botify/cdf/core/streams/base.py", line 117, in field_idx
    return map(lambda i: i[0], headers).index(field)
AttributeError: 'itertools.imap' object has no attribute 'index'
```

```
>       return filter(lambda i: i[0] == value, choices._triples)[0][1]
E       TypeError: 'itertools.ifilter' object has no attribute '__getitem__'

botify/frontend/apps/base/utils.py:128: TypeError
```

* replacing `unicode` with `str`
