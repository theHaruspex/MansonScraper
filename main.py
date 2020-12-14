import requests, bs4
from ebooklib import epub

def get_url_elements():
    archive_url = 'https://markmanson.net/archive'
    res = requests.get(archive_url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    url_elements = soup.select('.container table tbody tr td a')
    return url_elements

def filter_paid_articles(url_elements):
    filtered_url_elements = []
    for i, element in enumerate(url_elements):
        if 'subscribe' in str(element):
            target_element = url_elements[i - 1]
            filtered_url_elements.remove(target_element)
        else:
            filtered_url_elements.append(element)
    return filtered_url_elements

def compile_urls_from_element_list(element_list):
    manson_address = 'https://markmanson.net'
    urls = []
    for element in element_list:
        if 'https://markmanson.net/brazil_pt' in str(element):
            continue
        str_element = str(element)
        target_index_1 = str_element.index('"') + 1
        pre_url = str_element[target_index_1:]
        target_index_2 = pre_url.index('"')
        url = manson_address + pre_url[:target_index_2]
        urls.append(url)
    return urls

def get_title_from_element(element):
    element = str(element)
    target_index_1 = element.index('>') + 1
    pre_title = element[target_index_1:]
    target_index_2 = pre_title.index('<')
    title = pre_title[:target_index_2]
    return title

def get_article_content(url):
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    article_elements = soup.select('.pf-content p')
    title_element = soup.select('title')
    title = get_title_from_element(title_element)
    article_elements[0] = f'<h1>{title}</h1>'
    article_content = ''
    for element in article_elements:
        article_content += str(element)
    return title, article_content

def get_all_article_content():
    url_elements = get_url_elements()
    filtered_url_elements = filter_paid_articles(url_elements)
    url_list = compile_urls_from_element_list(filtered_url_elements)
    all_article_content = []
    for url in url_list:
        content = get_article_content(url)
        all_article_content.append(content)
    return all_article_content

def write_epub():
    article_content_list = get_all_article_content()
    book = epub.EpubBook()
    book.set_identifier('id310626')
    book.set_language('en')
    book.add_author('Mark Manson')

    chapter_list = []
    for i, article in enumerate(article_content_list):
        chapter_title = article[0]
        chapter_content = article[1]

        chapter = epub.EpubHtml(title=chapter_title, file_name=str(i),
                                lang='en')
        chapter_list.append(chapter)
        chapter.content = chapter_content
        book.add_item(chapter)

    book.spine = ['nav'] + chapter_list
    book.toc = tuple(chapter_list)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    style = 'BODY {color:white;}'
    nav_css = epub.EpubItem(uid='style_nav', file_name='style/nav.css',
                            media_type='text/css', content=style)
    book.add_item(nav_css)
    epub.write_epub('Manson.epub', book, {})

write_epub()
print('done')