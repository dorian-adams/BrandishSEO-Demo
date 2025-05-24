from django.forms import ValidationError
from docx import Document


def extract_tasks_docx(strategy_doc):
    """
    Extracts and validates structured tasks from a Word document.

    Raises:
        ValidationError: If a task is incomplete or contains duplicate keys.

    Returns:
        List[Dict[str, str]]: A list of validated task dictionaries.
    """
    DESIRED_KEYS = {"title", "priority", "description"}
    tasks = []
    task = {}

    for key, value in yield_task_fields_docx(strategy_doc):
        if key in task:
            raise ValidationError(
                f"Document is malformed. Duplicate key, '{key}', found before completing task group."
            )

        task[key] = value

        if DESIRED_KEYS.issubset(task.keys()):
            tasks.append(task)
            task = {}

    if task:
        raise ValidationError(
            f"Incomplete task found, missing: {DESIRED_KEYS - task.keys()}"
        )

    return tasks


def yield_task_fields_docx(strategy_doc):
    """
    Parse the project's ``strategy_doc`` for tasks, yielding each task component as a (key, value) pair.

    Only intended to be used when an xlsx document is not possible/not available.

    The method expects a Word document structured as:
    * Task Title in “Heading 2”
    * Priority Level (“High”, “Medium”, or “Low”) in “Heading 3”
    * One or more description paragraphs in “Normal”
    * Any other style (e.g. “Implementation Instructions” in Heading 4) to end the current task

    Yields:
        Tuple[str, str]: A sequence of (key, value) pairs, where key is one of:
            - "title" (str): the task's title (Heading 2 text, trailing ':' stripped)
            - "priority" (str): the priority level
            - "description" (str): the full description text (joined from consecutive Normal paragraphs within each Task)
    """
    doc = Document(strategy_doc)

    TASK_STYLE = "Heading 2"
    PRIORITY_STYLE = "Heading 3"
    DESCRIPTION_STYLE = "Normal"
    ACCEPTED_STYLES = {TASK_STYLE, PRIORITY_STYLE, DESCRIPTION_STYLE}

    paras = doc.paragraphs
    desc_paras = []
    collecting_task = False
    collecting_desc = False

    for p in paras:
        style = p.style.name
        text = p.text.strip()

        if collecting_desc and style != DESCRIPTION_STYLE:
            desc = " ".join(desc_paras)
            yield ("description", desc)
            collecting_desc = False
            collecting_task = False
            desc_paras = []

        if not text or (style not in ACCEPTED_STYLES):
            continue

        if style == TASK_STYLE and "task" in text.lower():
            collecting_task = True
            yield ("title", text.rstrip(":"))

        elif style == PRIORITY_STYLE:
            yield ("priority", text.split()[1])

        elif style == DESCRIPTION_STYLE and collecting_task:
            collecting_desc = True
            desc_paras.append(text)
