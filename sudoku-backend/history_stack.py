### Done by Danny Goldblum with help from Mintesnot Kassa ###

class HistoryStack:
    def __init__(self):
        self.stack = []

    def push(self, action, puzzle_state):
        """
        Push an action and the resulting puzzle state onto the stack.
        :param action: A description of the action (e.g., "Set cell (0, 0) to 5").
        :param puzzle_state: A snapshot of the puzzle grid.
        """
        self.stack.append({
            "action": action,
            "puzzle_state": puzzle_state
        })

    def pop(self):
        """
        Pop the most recent action and puzzle state from the stack.
        :return: A dictionary with "action" and "puzzle_state", or None if the stack is empty.
        """
        if self.stack:
            return self.stack.pop()
        return None

    def peek(self):
        """
        View the most recent action without removing it.
        :return: A dictionary with "action" and "puzzle_state", or None if the stack is empty.
        """
        if self.stack:
            return self.stack[-1]
        return None

    def clear(self):
        """Clear the history stack."""
        self.stack = []
