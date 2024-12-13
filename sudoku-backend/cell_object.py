### Done by Danny Goldblum ###

class SudokuCell:
    def __init__(self, location: tuple, correct_value: int):
        self._location = location  # Tuple (row, column)
        self._correct_value = correct_value
        self._inserted_value = None  # Value inserted by the user
        self._is_correct = False  # True if the inserted value matches the correct value
        self._is_initialized = False  # True if the cell starts with a value
        self._notes = []  # List for user notes

    # Getter and Setter for location
    def get_location(self):
        return self._location

    def set_location(self, location: tuple):
        self._location = location

    # Getter and Setter for correct value
    def get_correct_value(self):
        return self._correct_value

    def set_correct_value(self, correct_value: int):
        self._correct_value = correct_value
        #This may need to change based on solving algo
    # Getter and Setter for inserted value
    def get_inserted_value(self):
        return self._inserted_value

    def set_inserted_value(self, inserted_value: int):
        if self._inserted_value == inserted_value:
            self._inserted_value = None
        else:
            self._inserted_value = inserted_value
        self._is_correct = inserted_value == self._correct_value

    # Getter and Setter for is_correct
    def get_is_correct(self):
        return self._is_correct

    # Getter and Setter for is_initialized
    def get_is_initialized(self):
        return self._is_initialized

    def set_is_initialized(self, is_initialized: bool):
        self._is_initialized = is_initialized

    # Getter and Setter for notes
    def get_notes(self):
        return self._notes

    def set_notes(self, notes: list):
        self._notes = notes

    def add_note(self, note: int):
        if note not in self._notes:
            self._notes.append(note)

    def remove_note(self, note: int):
        if note in self._notes:
            self._notes.remove(note)
