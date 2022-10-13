import types


def override(target_cls, replacement_condition_fn=None):
    class Meta(type):
        def __new__(mcls, name, bases, new_ns):
            if not bases:
                return super().__new__(mcls, name, bases, new_ns)
            old_ns = {}
            for key, val in new_ns.items():
                if key in ('__module__', '__qualname__'):
                    continue
                old_val = target_cls.__dict__.get(key)
                if old_val is not None:
                    old_ns[key] = old_val
                replacement = ReplacementDesc(val, old_val, replacement_condition_fn)
                replacement.name = key
                setattr(target_cls, key, replacement)
            return types.SimpleNamespace(**old_ns)

    class ExtendMe(metaclass=Meta):
        pass

    return ExtendMe


class ReplacementDesc:

    def __init__(self, replacement, target, condition_fn=None):
        self.target = target
        self.replacement = replacement
        self.condition_fn = condition_fn

    def __get__(self, instance, owner):
        if not self.condition_fn or self.condition_fn():
            try:
                self.replacement.__get__
            except AttributeError:
                return self.replacement
            else:
                return self.replacement.__get__(instance, owner)
        if not self.target:
            raise AttributeError
        try:
            self.target.__get__
        except AttributeError:
            return self.target
        else:
            return self.target.__get__(instance, owner)


if __name__ == '__main__':
    class C:
        x = 1

        @classmethod
        def f(cls):
            return cls.x + 1
    #
    class C1(override(C)):
        @classmethod
        def f(cls):
            f = C1.f.__get__(None, cls)
            return f() + 1

    assert C.f() == 3
