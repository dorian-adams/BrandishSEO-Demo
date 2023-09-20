import zipfile
import xml.etree.ElementTree as ET
import re


def extract_tasks(instance):
    doc = zipfile.ZipFile(instance.strategy_doc).read("word/document.xml")
    root = ET.fromstring(doc)
    string_doc = ET.tostring(root, encoding="utf-8")
    # Extract text only from the xml.
    text = re.findall(
        r'(?:<ns0:t xml:space="preserve">)([^<]*)', string_doc.decode("utf-8")
    )

    tasks = []
    task_info = {"title": None}
    iter_list = iter(text)
    new_task = False
    for line in iter_list:
        if "Implementation Instructions" in line:
            # 'Implementation Instructions' marks the end of each group of Tasks
            new_task = False
            continue
        elif "Task" in line:
            if task_info["title"] is not None and task_info not in tasks:
                tasks.append(task_info)
            task_info = {"title": line, "priority": next(iter_list), "description": ""}
            new_task = True
        elif new_task:
            task_info["description"] += line
    tasks.append(task_info)
    return tasks
