import time, random

x = random.sample(range(50000),10000)
y = random.sample(range(50000),10000)

tic = time.time()
w1 = [elem for elem in x if elem==elem in y]
toc = time.time()
print(toc-tic)

tic = time.time()
w2 = set(x).intersection(y)
toc = time.time()
print(toc-tic)

print(len(w1))
print(len(w2))