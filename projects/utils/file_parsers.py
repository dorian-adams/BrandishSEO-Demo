from django.forms import ValidationError
from docx import Document

import pandas as pd


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
                f"Document is malformed. Duplicate key, '{key}', found before"
                " completing task group."
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
    Parse the project's ``strategy_doc`` for tasks, yielding each task 
    component as a (key, value) pair.

    Only intended to be used when an xlsx strategy document is not available.

    Expects a Word document structured as:
    * Task Title in “Heading 2”.
    * Priority Level (“High”, “Medium”, or “Low”) in “Heading 3”.
    * One or more description paragraphs in “Normal”.
    * Any other style (e.g. “Implementation Instructions” in Heading 4) to end 
      the current task.

    Args:
        strategy_doc: The strategy Doc (.docx) file.

    Yields:
        Tuple[str, str]: A sequence of (key, value) pairs, where key is one of:
            - "title" (str): the task's title (Heading 2 text).
            - "priority" (str): the priority level.
            - "description" (str): the full description text (joined).
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


def extract_tasks_xlsx(strategy_xlsx):
    """
    Parse the project's strategy Excel file to extract tasks from all relevant 
    sheets.

    This is the preferred extraction method when available.
    Processes all sheets except 'Descriptions', which doesn't contain tasks. 
    Validates the presence of required columns and data completeness.

    Args:
        strategy_xlsx: The strategy Excel (.xlsx) file

    Raises:
        ValidationError: If any sheet:
            - Is missing the required columns.
            - Contains incomplete tasks.

    Returns:
        List[Dict[str, str]]: A list of validated task dictionaries.
    """
    REQUIRED_COLS = {"Task Title", "Priority", "Description"}
    OUTPUT_MAP = {
        "Task Title": "title",
        "Priority": "priority",
        "Description": "description",
    }
    tasks = []

    with pd.ExcelFile(strategy_xlsx) as xls:
        for sheet_name in xls.sheet_names:
            if sheet_name == "Descriptions":
                continue

            df = xls.parse(
                sheet_name=sheet_name,
                header=1,
                usecols=REQUIRED_COLS,
            )

            if not REQUIRED_COLS.issubset(df.columns):
                raise ValidationError(
                    f"Sheet '{sheet_name}' is missing required columns."
                )

            clean_df = df.dropna(how="all").rename(columns=OUTPUT_MAP)

            if clean_df.isna().values.any():
                raise ValidationError(
                    "Incomplete task(s) found on the following sheet:"
                    f" {sheet_name}"
                )

            tasks.extend(clean_df.to_dict(orient="records"))

    return tasks
