class ViscaException(RuntimeError):
    """Raised when the camera doesn't like a message that it received"""

    def __init__(self, response_body):
        status_code = response_body[2]
        descriptions = {
            1: 'Message length error',
            2: 'Syntax error',
            3: 'Command buffer full',
            4: 'Command cancelled',
            5: 'No socket',
            0x41: 'Command not executable'
        }

        super().__init__(f'Error when executing command: {descriptions[status_code]}')
