'''
init_state？随机选一个点作为区块0
state? 当前分块情况
action? 要么创建一个新区块（随机），要么扩展一个已有的区块（向一个方向）
reward？当前区块数+未分块像素数-SUM（每个像素的颜色偏差*惩罚因数）
default_policy？无错扩展
tips：大区块覆盖小区块，可以删掉小区块；区块线性次序
'''