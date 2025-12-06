class TwilioError(Exception):
    def __init__(self, error, *args):
        self.error = error
        super().__init__(*args)
    