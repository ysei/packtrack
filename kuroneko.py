# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
from tracker import yamato

numbers = ["225303520584", "249790484403"]

page2 = yamato.get_detail_page(numbers)

f = open("page2.html", "wb")
f.write(page2)
f.close()