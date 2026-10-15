import io

from ruditor_py.agent import Agent

AI_MODEL = "google/gemma-4-e4b"
URL = "http://127.0.0.1:1234/v1"

a_fixer = Agent(reasoning="low", url=URL, model=AI_MODEL, sys_prompt=f"Ты правишь текст, делая его более читабельным. Не добавляя никаких коментов от себя.")
a_validator = Agent(reasoning="low", url=URL, model=AI_MODEL, sys_prompt=f"Ты проверяешь смысл текста. И если смысл непонятен правишь. К примеру \"На дереве сидел дом Оли\". Явно бред. Надо сделать \"На дереве сидела Оля\". И прочее.")

async def validate_sense(old_text: str, new_text: str):
    a_validator.reset()
    resp = await a_validator.query(f"Проверь новый текст. Если всё ок, тогда ответь одним символом \"0\", если нет, тогда просто без коментаривев вышли исправленную версию нового текста. \n\n# Оригинал:\n{old_text}\n\n# Новый текст:\n{new_text}")
    if len(resp) < 5 or resp.startswith("0"):
        return new_text
    return resp

async def parse_text(text_name, text_out_name):
    new_lines = []
    text = None

    # Reading the file
    with io.open(text_name, 'r', encoding='UTF-8') as f:
        text = f.read()

    lines = text.split("\n")
    for line in lines:
        line = line.strip()

        if len(line) < 1:
            new_lines.append(line)
            continue

        print(line)

        a_fixer.reset()
        is_err = await a_fixer.query(f"Проанализируй и скажи, стоит ли исправлять?: {line}\n\nОтветь либо \"Y\" либо \"N\"")
        if is_err.lower() == "y":
            changed = await a_fixer.query("Тогда пришли мне исправленную версию")
            changed = await validate_sense(line, changed)
            new_lines.append(changed)
            print(f"CORRECTED: {changed}\n")
        else:
            new_lines.append(line)
            print(f"OK")

    with io.open(text_out_name, 'w', encoding='UTF-8') as f:
        f.write("\n".join(new_lines))