from celery.task.control import inspect


# def setup_task(service):
#     service.app = app
#     print(service)
#     result = None
#     if service.query_predicate == self.NS.whyis.globalChangeQuery:
#         result = process_resource
#     else:
#         result = process_nanopub
#     result.service = lambda : service
#     return result


def is_running_waiting(service_name):
    """
    Check if a task is running or waiting.
    """
    if is_waiting(service_name):
        return True
    active = inspect().active()
    if active:
        running_tasks = list(active.values())[0]
        for task in running_tasks:
            if 'kwargs' in task:
                args = eval(task['kwargs'])
                if service_name == args.get('service_name',None):
                    return True
    return False


def is_waiting(service_name):
    """
    Check if a task is waiting.
    """
    scheduled = inspect().scheduled()
    if scheduled:
        scheduled_tasks = list(scheduled.values())[0]
        for task in scheduled_tasks:
            if 'kwargs' in task:
                args = eval(task['kwargs'])
                if service_name == args.get('service_name',None):
                    return True
    return False


def is_waiting_importer(entity_name, exclude=None):
    """
    Check if a task is running or waiting.
    """
    if inspect().scheduled():
        tasks = list(inspect().scheduled().values())
        for task in tasks:
            if 'args' in task and entity_name in task['args']:
                return True
    return False
