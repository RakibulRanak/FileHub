from collections import deque

# deque is for implementing queue
# Stack is like a list

stack = []

for i in range(3):
    x = int(input())
    stack.append(x)

print(stack)

stack.pop()
print(stack)

stack.pop()
print(stack)

print(stack.pop())

queue = deque([])

for i in range(5):
    x = int(input())
    queue.append(x)

print(queue)

print(queue)

print(deque.popleft())

queue.popleft()
print(queue[0])