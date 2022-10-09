import types
from functools import cached_property

function = type(lambda: None)


class overriden:
    def __init__(self, target_cls):
        self.target_cls = target_cls

    @cached_property
    def meta(self):
        class Meta(type):
            def __new__(mcls, name, bases, new_ns):
                old_ns = {}
                for key, val in new_ns.items():
                    if key in ('__module__', '__qualname__'):
                        continue
                    old_val = self.target_cls.__dict__.get(key)
                    if old_val is not None:
                        old_ns[key] = old_val
                    setattr(self.target_cls, key, ReplacementDesc(val, old_val))
                return types.SimpleNamespace(**old_ns)

        return Meta


class ReplacementDesc:

    def __init__(self, replacement, target, condition: function=None):
        self.target = target
        self.replacement = replacement
        self.condition = condition

    def __get__(self, instance, owner):
        if not self.condition or self.condition():
            return self.replacement.__get__(instance, owner)
        if not self.target:
            raise AttributeError
        return self.target.__get__(instance, owner)


if __name__ == '__main__':
    class C:
        def f(self):
            return 1

    C1 = overriden(C)

    class C2(metaclass=C1.meta):
        def f(self):
            return 2

    assert C().f() == 2