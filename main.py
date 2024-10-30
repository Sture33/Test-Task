import json, fitz

nn = [
    '\uf0a7 Определение порядка переделов, если в учетной политике установлен автоматический способ определения порядка подразделений для закрытия счетов затрат. Если установлен ручной способ, то порядок закрытия счета 2000 «Основное производство» по подразделе...',
    '\uf0a7 Списание расходов основного и вспомогательного производства на себестоимость выпуска: для продукции - пропорционально плановым ценам; для услуг, оказанных сторонним заказчикам, пропорционально плановым ценам или по выручке в зависимости от настроек ...',
    '\uf0a7 Списание общепроизводственных расходов на расходы основного и вспомогательного производства.',
    '\uf0a7 Корректировка выпуска на разницу между плановой и фактической стоимостью.']

ext = []
structure = {}


def normalize(text):
    return ' '.join(text.split())


with fitz.open('Read.pdf') as doc:
    for i in range(doc.page_count):
        page = doc[i]
        ext.append(normalize(page.get_text()))
    galleys = doc.get_toc()
    new_galleys = []
    texts = []

    for i in range(len(galleys)):
        if 'Глава' in galleys[i][1] or nn[0] in galleys[i][1] or nn[1] in galleys[i][1] or nn[2] in galleys[i][1] or nn[3] in galleys[i][1]:
            continue
        else:
            new_galleys.append(galleys[i])

    for i in range(len(new_galleys)):

        if i < len(new_galleys) - 1:
            start_pos = new_galleys[i][2]
            end_pos = new_galleys[i + 1][2]
            pre_start_pos = normalize(ext[new_galleys[i][2] - 1]).find(normalize(new_galleys[i][1]))
            pre_end_pos = normalize(ext[new_galleys[i + 1][2] - 1]).find(normalize(new_galleys[i + 1][1]))
            if pre_start_pos == -1:
                pre_start_pos = normalize(ext[new_galleys[i][2] - 1]).find(normalize(new_galleys[i][1]).upper())
            if pre_end_pos == -1:
                pre_end_pos = normalize(ext[new_galleys[i + 1][2] - 1]).find(normalize(new_galleys[i + 1][1]).upper())

            sst = ext[start_pos - 1][pre_start_pos:]
            est = ext[end_pos - 1][:pre_end_pos]

            if start_pos != end_pos:
                tst = ''.join(ext[start_pos:end_pos - 1])
                texts.append(''.join([sst,tst,est]))

            elif start_pos == end_pos:
                sst = ext[start_pos - 1][pre_start_pos:pre_end_pos]
                texts.append(''.join([sst]))
        else:
            start_pos = new_galleys[-1][2]
            pre_start_pos = normalize((ext[new_galleys[-1][2] - 1]).lower()).index(
                normalize((new_galleys[-1][1]).lower()))
            sst = ext[start_pos - 1][pre_start_pos:]
            est = ext[-1]
            texts.append(''.join([sst, est]))

        if new_galleys[i][0] == 1:
            structure[f"{new_galleys[i][1]}"] = {'text': f'{texts[i]}', 'sections': {}}

        elif new_galleys[i][0] == 2:
            last_key = list(structure.keys())[-1]
            structure[f'{last_key}']['sections'][f'{new_galleys[i][1]}'] = {'text': f'{texts[i]}',
                                                                   'subsections': {}}
        elif new_galleys[i][0] == 3:
            last_key_of_last_key = list(structure[f'{last_key}']['sections'].keys())[-1]
            structure[f'{last_key}']['sections'][f'{last_key_of_last_key}']['subsections'][f'{new_galleys[i][1]}'] = {
                'text': f'{texts[i]}',
                'subsubsections': {}}
        elif new_galleys[i][0] == 4:
            last_key_of_last_key_of_last_key = \
                list(structure[f'{last_key}']['sections'][f'{last_key_of_last_key}']['subsections'].keys())[-1]
            structure[f'{last_key}']['sections'][f'{last_key_of_last_key}']['subsections'][
                f'{last_key_of_last_key_of_last_key}']['subsubsections'][f'{new_galleys[i][1]}'] = {
                'text': f'{texts[i]}', }

    data = json.dumps(structure, indent=4, ensure_ascii=False)
    data = json.loads(str(data))
    with open('structure.json', 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)