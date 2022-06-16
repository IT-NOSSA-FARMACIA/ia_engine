EXECUTION_STATUS_PENDING = "PE"
EXECUTION_STATUS_QUEUE = "QU"
EXECUTION_STATUS_QUEUE_RETRY = "RT"
EXECUTION_STATUS_PROCESSING = "PR"
EXECUTION_STATUS_SUCCESS = "SC"
EXECUTION_STATUS_ERROR = "ER"
EXECUTION_STATUS_CREATING_TICKET = "CT"


EXECUTION_STATUS_CHOICE = (
    (EXECUTION_STATUS_PENDING, "Pending"),
    (EXECUTION_STATUS_PROCESSING, "Processing"),
    (EXECUTION_STATUS_SUCCESS, "Success"),
    (EXECUTION_STATUS_ERROR, "Error"),
    (EXECUTION_STATUS_QUEUE, "Queue"),
    (EXECUTION_STATUS_QUEUE_RETRY, "Queue (Retry)"),
    (EXECUTION_STATUS_CREATING_TICKET, "Creating tickets"),
)

NOTIFICATION_TYPE_NEVER = "NE"
NOTIFICATION_TYPE_ERROR = "ER"
NOTIFICATION_TYPE_SUCCESS = "SC"
NOTIFICATION_TYPE_ALL = "AL"


NOTIFICATION_TYPE_CHOICE = (
    (NOTIFICATION_TYPE_NEVER, "Nunca"),
    (NOTIFICATION_TYPE_ERROR, "Apenas Erro"),
    (NOTIFICATION_TYPE_SUCCESS, "Apenas Sucesso"),
    (NOTIFICATION_TYPE_ALL, "Sempre"),
)
