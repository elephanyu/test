# coding: utf-8
# 协程在2.5版本引入 PEP342
# 在3.3版本对生成器进行了两处改进 PEP380，以便更好的作为协程使用
# 1、生成器可以返回一个值，以前的版本在生成器中给return语句提供值，会抛出SyntaxError
# 2、新引入yield from语法，使它可以把复杂的生成器重构成小型的嵌套生成器，省去了把生成器的工作委派给子生成器所需的大量样板代码
# yield from 用于简化for循环中的yield表达式
# def gen():
#     for c in 'AB':
#         yield c
#     for i in range(1,3):
#         yield i
# 可以简写为：
# def gen():
#     yield from 'AB'
#     yield from range(1,3)
# 下面是yield from的实现伪代码
# RESULT = yield from EXPR
# yield from处理客户端（调用方）的.throw(xx)和.close()方法(子生成器是纯粹的迭代器，不支持这两个方法)
# 用于自动预激的装饰器与yield from不兼容
import sys

if __name__ == '__main__':
    # EXPR 任何可迭代的对象
    # _i 迭代器(子生成器)
    # _y 产出的值(子生成器的值)
    # _r 结果(子生成器运行结束后yield from表达式的值)
    # _s 发送的值(调用方发送给委派生成器的值，这个值会转发给子生长期)
    # _e 异常(异常对象，在这段简化伪代码中始终是StopIteration的实例)
    EXPR = 'abcde'
    _i = iter(EXPR)
    try:
        _y = next(_i)
    except StopIteration as _e:
        _r = _e.value
    else:
        while 1:
            try:
                _s = yield _y
            except GeneratorExit as _e:
                try:
                    _m = _i.close()
                except AttributeError:
                    pass
                else:
                    _m()
                raise _e
            except BaseException as _e:
                _x = sys.exc_info()
                try:
                    _m = _i.throw
                except AttributeError:
                    raise _e
                else:
                    try:
                        _y = _m(*_x)
                    except StopIteration as _e:
                        _r = _e.value
                        break
            else:
                try:
                    if _s is None:
                        _y = next(_i)
                    else:
                        _y = _i.send(_s)
                except StopIteration as _e:
                    _r = _e.value
                    break
    RESULT = _r
