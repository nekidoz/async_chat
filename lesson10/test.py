class SomeData:
    some_var: str

SomeData.some_var = "some var"
inst = SomeData()
print("1. ", inst.some_var)
print("2. ", SomeData.some_var)
inst.some_var = "other var"
print("3. ", inst.some_var)
print("4. ", SomeData.some_var)
