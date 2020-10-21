class Node():
    def __init__(self, star_1_id, movie_id, star_2_id):
        self.star_1_id = star_1_id
        self.star_2_id = star_2_id
        self.movie_id = movie_id


class Stack():
    def __init__(self):
        self.frontier = []
        self.all_paths = []

    def push(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.star_2_id == state for node in self.frontier)

    def isEmpty(self):
        return len(self.frontier) == 0

    def pop(self):
        if self.isEmpty():
            raise Exception('Stack is empty.')
        else:
            return self.frontier.pop()

    def show(self):
        return self.frontier

    def peek(self):
        if self.isEmpty():
            raise Exception('Stack is empty.')
        else:
            return self.frontier[-1]


class Queue(Stack):
    def pop(self):
        if self.isEmpty():
            raise Exception('Queue is empty')
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

    def peek(self):
        if self.isEmpty():
            raise Exception('Queue is empty')
        else:
            return self.frontier[0]