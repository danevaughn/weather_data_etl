
class NoDataException(Exception):
    
    def __init__(self) -> None:
        super().__init__()
        self.message = 'Invalid Pub/Sub message, lacking data information.'
    
    def __str__(self) -> str:
        return self.message



class FailedBigQueryJob(Exception):
    
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message
    
    def __str__(self) -> str:
        return f'There was some error during BigQuery load job. Error body: {self.message}'