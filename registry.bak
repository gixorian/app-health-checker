# The central brain where all tasks are mapped
TASK_REGISTRY = {}


def register_task(name, func):
    """
    Call this to 'plug in' a new capability to the Nerva engine.
    Example: register_task("SEND_EMAIL", my_email_function)
    """
    TASK_REGISTRY[name] = func
    print(f"Nerva: Registered task '{name}'")
