class ViscaException(RuntimeError):
    """Raised when the camera doesn't like a message that it received"""

    def __init__(self, response_body):
        status_code = response_body[2].hex()
        descriptions = {
            '01': 'Message length error',
            '02': 'Syntax error',
            '03': 'Command buffer full',
            '04': 'Command cancelled',
            '05': 'No socket',
            '41': 'Command not executable'
        }

        super().__init__(f'Error when executing command: {descriptions[status_code]}')
