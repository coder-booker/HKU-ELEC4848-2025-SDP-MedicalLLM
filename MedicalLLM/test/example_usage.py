from enum import Enum

class test(str, Enum):
    A = "a"
    B = "b"

bruh = {
    test.A: "hello",
}
print(test.A)
print(test.A == 'a')

if test.A in bruh:
    print("yes")