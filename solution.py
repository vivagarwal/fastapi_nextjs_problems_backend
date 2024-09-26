def sol_0(y: str) -> bool:
    x = int(y)
    if x < 0 or (x > 0 and x % 10 == 0):
        return False
    sum = 0
    while x > sum:
        sum = (sum * 10) + x % 10
        x = x // 10
    return (sum // 10 == x or sum == x)

def sol_1(y: str):
    return "aayush"+y