__author__ = 'nikita_kartashov'


def accepts(*types):
    def check_accepts(f):
        assert len(types) == f.func_code.co_argcount

        def new_f(*args, **kwargs):
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                    "arg %r does not match %s" % (a, t)
            return f(*args, **kwargs)

        new_f.func_name = f.func_name
        return new_f

    return check_accepts


def returns(return_type):
    def check_returns(f):
        def new_f(*args, **kwargs):
            result = f(*args, **kwargs)
            assert isinstance(result, return_type), \
                "return value %r does not match %s" % (result, return_type)
            return result
        return new_f

    return check_returns