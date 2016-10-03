from bitarray import bitarray

arr = {1: bitarray('00000'), 2: bitarray('11010'), 3: bitarray('11100')}

flag = "trure"
for i in arr:
    if any(arr[i]):
        print(flag, arr[i])

