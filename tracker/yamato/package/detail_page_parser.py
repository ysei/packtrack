# -*- coding: utf-8 -*-

import re
from BeautifulSoup import BeautifulSoup

# 詳細ページ解析クラス
class DetailPageParser:
  def __init__(self):
    pass

  @classmethod
  def trim_script_tag(cls, html):
    pattern = re.compile(r"<script.+?>.+?</script>", re.IGNORECASE | re.DOTALL)
    return re.sub(pattern, "", html)

  @classmethod
  def trim_style_tag(cls, html):
    pattern = re.compile(r"<style.+?>.+?</style>", re.IGNORECASE | re.DOTALL)
    return re.sub(pattern, "", html)

  @classmethod
  def trim_center_tag(cls, html):
    pattern = re.compile(r"</?center>", re.IGNORECASE)
    return re.sub(pattern, "", html)

  @classmethod
  def trim_paragraph_tag(cls, html):
    pattern = re.compile(r"(?:<p.*?>|</p>)", re.IGNORECASE)
    return re.sub(pattern, "", html)

  @classmethod
  def trim_bold_tag(cls, html):
    pattern = re.compile(r"</?b>", re.IGNORECASE)
    return re.sub(pattern, "", html)

  @classmethod
  def trim_unwanted_tags(cls, html):
    result1 = cls.trim_script_tag(html)
    result2 = cls.trim_style_tag(result1)
    result3 = cls.trim_center_tag(result2)
    result4 = cls.trim_paragraph_tag(result3)
    result5 = cls.trim_bold_tag(result4)
    return result5

  @classmethod
  def trim_unwanted_nodes(cls, doc):
    # ヘッダを削除
    for i in range(4):
      doc.body.table.extract()
    doc.body.form.extract()
    for i in range(4):
      doc.body.table.extract()

    # フッタを削除
    doc.body.findAll("table", recursive = False)[-1].extract()

    # リンクを削除
    for elem in doc.body.findAll("a", {"name": re.compile(".+")}):
      elem.extract()
    for elem in doc.body.findAll("a", {"href": re.compile("^#")}):
      elem.extract()

    # ボタンを削除
    for elem in doc.body.findAll("div", {"class": "print_hide"}):
      elem.extract()

    # 水平線を削除
    for elem in doc.body.findAll("hr"):
      elem.extract()

    # 強制改行を削除
    for elem in doc.body.findAll("br"):
      elem.extract()

  @classmethod
  def create_doc(cls, html):
    src = cls.trim_unwanted_tags(html)
    doc = BeautifulSoup(src)
    cls.trim_unwanted_nodes(doc)
    return doc

  @classmethod
  def search_tracking_number_elements(cls, doc):
    pattern = re.compile(r"^\d+-\d+-\d+$")
    elements = []
    for element in doc.body.findAll("font", size = "4"):
      if pattern.match(element.string):
        elements.append(element)
    return elements

  @classmethod
  def parse(cls, html):
    doc = cls.create_doc(html)

    tracking_number_elements = cls.search_tracking_number_elements(doc)

    records = []
    for tracking_number_element in tracking_number_elements:
      message_table     = tracking_number_element.nextSibling.nextSibling
      detail_table      = message_table.nextSibling.nextSibling
      detail_list_table = detail_table.nextSibling.nextSibling

      record = {
        u"伝票番号": tracking_number_element.string,
      }
      record.update(cls.parse_message_table(message_table))
      record.update(cls.parse_detail_table(detail_table))
      record.update(cls.parse_detail_list_table(detail_list_table))
      records.append(record)

    return {"一覧": records}

  @classmethod
  def parse_message_table(cls, table):
    return {
      u"メッセージ": "\n".join(table.tr.td.contents),
    }

  @classmethod
  def parse_detail_table(cls, table):
    rows  = table.findAll("tr", recursive = False)
    cells = rows[1].findAll("td", recursive = False)

    return {
      u"商品名"        : cells[0].contents[0],
      u"お届け予定日時": cells[1].contents[0],
    }

  @classmethod
  def parse_detail_list_table(cls, table):
    results = []

    for row in table.findAll("tr", recursive = False)[1:]:
      cells = row.findAll("td", recursive = False)
      station_name_cell = cells[3]
      if station_name_cell.find("a") is None:
        station_name = station_name_cell.contents[0]
      else:
        station_name = station_name_cell.a.contents[0]

      info = {
        u"荷物状況"    : cells[0].contents[0],
        u"日付"        : cells[1].contents[0],
        u"時刻"        : cells[2].contents[0],
        u"担当店名"    : station_name,
        u"担当店コード": cells[4].contents[0],
      }
      results.append(info)

    return {u"詳細": results}
