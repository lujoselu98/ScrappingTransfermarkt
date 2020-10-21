import requests
from scrapy.selector import Selector


def extract_cups(link, no_before="15"):
    print(link)
    headers = {'User-Agent': 'Custom'}
    res = requests.get(link, headers=headers)
    sel = Selector(text=res.content)
    parent = sel.css('div.large-4 > div.box  tbody tr')
    titulos_dict = dict()
    for element in parent:
        element_classes = element.css('::attr(class)').extract()
        if 'bg_Sturm' in element_classes:
            titulo = element.css('td::text')[0].extract()
            titulo = titulo.split('x')[1].strip()
            titulos_dict[titulo] = []
            # print(titulo)
        else:
            ano = element.css('td:nth-of-type(1) ::text')[0].extract()
            if '/' in ano:
                ano_splits = [int(x) for x in ano.split('/')]
                no_before_int = int(no_before)
                if any(ano_split < no_before_int for ano_split in ano_splits):
                    continue
            else:
                no_before_int = int('20' + no_before)
                if int(ano) < no_before_int:
                    continue
            texts = element.css('td:nth-of-type(3) ::text').extract()
            texts = [text for text in texts if '\n' not in text]
            texts = [text.strip() for text in texts if len(text.strip()) > 0]
            if len(texts) > 1:
                extra_info = texts[1:]
            else:
                extra_info = None
            if len(texts) > 0:
                equipo_o_liga = texts[0]
            else:
                equipo_o_liga = None
            single_cup = {'anno': ano, 'equipo_o_liga': equipo_o_liga, 'extra_info': extra_info}
            # print(f"{ano} -> {equipo_o_liga} -> {extra_info}")
            titulos_dict[titulo].append(single_cup)

    for key in titulos_dict.copy().keys():
        if len(titulos_dict[key]) == 0:
            del titulos_dict[key]
    return titulos_dict


if __name__ == '__main__':
    f = open('Raw_All_Players_Data_Links.txt', 'r')
    lines = f.readlines()
    links = [line.strip().split('->')[1].strip().replace('profil', 'erfolge') for line in lines]
    links = list(dict.fromkeys(links))
    for link in links:
        print(extract_cups(link))
