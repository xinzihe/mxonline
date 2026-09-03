import collections
import collections.abc

# 解决 Python 3.10+ 移除 collections.Iterable 导致 pure_pagination 报错的问题
collections.Iterable = collections.abc.Iterable