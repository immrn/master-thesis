import sys
import os
import toml

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from user_management import Users
import config

def send_task_email(path_to_html: str, bcc_list, subject: str, increment_counter: bool):
    PATH_DAILY_TASKS_TOML = "./scripts/daily_tasks.toml"

    tml = toml.load(PATH_DAILY_TASKS_TOML)
    tml["counter"] = tml["counter"] % len(tml["tasks"])

    print(f"task #{tml['counter']}")

    with open(path_to_html) as file:
        content = file.read()

    task = tml["tasks"][tml["counter"]]
    content = content.replace("{_webservice_name_}", config.WEBSERVICE_NAME)
    content = content.replace("{_recipient_}", task["recipient"])
    content = content.replace("{_value_}", str(task["value"]) + " €")
    content = content.replace("{_message_}", task["message"])

    if increment_counter:
        tml["counter"] += 1

    Users._send_email_(
        receiver_addr=config.SENDER_EMAIL_ADDRESS,
        subject=subject,
        html=content,
        bcc=bcc_list,
        sender_name="Nutzerstudie zu zeitbasierten Einmalpasswörtern",
        path_to_pw_file=config.PATH_TO_EMAIL_PW_FILE
    )

    with open(PATH_DAILY_TASKS_TOML, "w") as file:
        toml.dump(tml, file)