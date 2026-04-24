import re
with open('dashboard/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r',\s*paper_bgcolor=[\"\']white[\"\']', '', content)
content = re.sub(r'paper_bgcolor=[\"\']white[\"\']\s*,?', '', content)
content = re.sub(r',\s*plot_bgcolor=[\"\']white[\"\']', '', content)
content = re.sub(r'plot_bgcolor=[\"\']white[\"\']\s*,?', '', content)
content = re.sub(r',\s*gridcolor=[\"\']#eee[\"\']', '', content)
content = re.sub(r'gridcolor=[\"\']#eee[\"\']\s*,?', '', content)

with open('dashboard/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
