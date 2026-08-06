from verifica.fetcher import Fetcher

class Checker:
    def __init__(self, exercise):
        self.exercise = exercise
        self.fetcher = Fetcher(exercise)
        self.exercise_dir = None