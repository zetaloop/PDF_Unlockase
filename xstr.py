class _xstr(str):
    "带附件的字符串"
    def __new__(cls, value, more=None):
        obj = super().__new__(cls, value)
        obj.more = more
        return obj
    def __lshift__(self, more):
        self.more = more
        return self

class _xstr_factory:
    "附件字符串创建器"
    def __mul__(self, string):
        return _xstr(string)

xstr = _xstr_factory()

# return xstr* 'Some String' << [123456 ,'data1', 'data2']
# ... and use: xxx.more to get the extra data
# This is str compatible.