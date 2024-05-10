from datetime import datetime, timedelta
from .send_email import send_email

class ErrorReporter:
    def __init__(self):
        self.last_error_times = {}

    def report_error(self, error_message):
        current_time = datetime.now()

        if error_message not in self.last_error_times or current_time - self.last_error_times[error_message] >= timedelta(days=1):
            send_email("Error Report", error_message)
            self.last_error_times[error_message] = current_time

def main():
    error_reporter = ErrorReporter()
    error_message1 = "Help 1!"
    error_message2 = "Help 2!"
    
    error_reporter.report_error(error_message1)
    error_reporter.report_error(error_message1)
    error_reporter.report_error(error_message2)
    error_reporter.report_error(error_message2)

if __name__ == "__main__":
    main()