# coding: utf8
# 任何包含yield语句的函数成为生成器
# 生成器每次产生一个值（使用yield语句），函数就会被冻结，函数被重新唤醒后从停止的地方开始执行
# nested = [[1, 2], [3, 4], [5]]
# def flatten(nested):
#     for sublist in nested:
#         for element in sublist:
#             yield element
# list(flatten(nested))

def conflict(state, nextX):
    # state 前面皇后的水平位置
    # nextX 代表下一个皇后的水平位置
    # nextY 代表下一个皇后的垂直位置
    nextY = len(state)
    for i in range(nextY):
        # 下一个皇后和前面的皇后有桐乡的水平位置，或者在一条对角线上，就会发生冲突
        if abs(state[i] - nextX) in (0, nextY - i):
            return True
    return False

def queens(num=8, state=()):
    flag = 0
    for pos in range(num):
        if not conflict(state, pos):
            # 是最后一个皇后，不冲突时直接返回该位置
            if len(state) == num - 1:
                yield (pos,)
            else:
                # 否则递归运算出前面所有皇后的位置, 然后将所有皇后的位置返回
                for result in queens(num, state + (pos,)):
                    # 增加三行代码用于debug，便于理解
                    if len(result) == 7 and flag < 3:
                        print (pos,) + result
                    flag += 1
                    yield (pos,) + result

def prettyprint(solution):
    def line(pos, length=len(solution)):
        return '- ' * (pos) + '* ' + '- ' * (length - pos - 1)
    for pos in solution:
        print line(pos)

if __name__ == '__main__':
    results = list(queens(8))
    print results[:3]
