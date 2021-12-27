class ViscaException(RuntimeError):
    """Raised when the camera doesn't like a message that it received"""

    def __init__(self, response_body):
        self.status_code = response_body[2]
        descriptions = {
            1: 'Message length error',
            2: 'Syntax error',
            3: 'Command buffer full',
            4: 'Command cancelled',
            5: 'No socket',
            0x41: 'Command not executable'
        }
        self.description = descriptions[self.status_code]

        super().__init__(f'Error when executing command: {self.description}')


class NoQueryResponse(TimeoutError):
    """Raised when a response cannot be obtained to a query after a number of retries"""
