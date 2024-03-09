#!/user/bin/python3
import logging
logger = logging.getLogger(__name__)

import pandas as pd
from typing import Tuple

#
# リダイレクトのチェック
#
def testRedirection(url):
    import requests
    res = requests.get(url)
    if res.history != []:
        if res.history[0].status_code == 302:
            return True
    return False

#
# 結果をファイルにキャッシュする
#
import percache, os

#CACHE_FILE = '~/Library/Preferences/exchangeRate-cache'
CACHE_FILE = '/tmp/exchangeRate-cache'
exCache = percache.Cache(os.path.expanduser(CACHE_FILE))

#
# UFJ銀から為替レートを取得する
#
@exCache
def getHistoricalCurrency(targetCurrency, targetDate) -> Tuple[float, float, float, float]:
    import re
    logger.info(f"Getting historical currency first time at date: {targetDate}")
    content = targetDate
    pattern = '(\d+)/(\d+)/(\d+)'
    result = re.match(pattern, content)
    if not result:
        logger.error(f"The format of date \'{targetDate}\' might be wrong.\n\n")
        return
    theDate = ("20"+result.group(1))[-2:]+("0"+result.group(2))[-2:]+("0"+result.group(3))[-2:]
    base_url = 'https://www.murc-kawasesouba.jp/fx/past/index.php'
    param_url = '?id='
    # UFJ銀は11:00AMにデータを更新するが、データがなかった場合はリダイレクトして本日のデータのページに飛んでしまう。
    if testRedirection(base_url+param_url+theDate):
        logger.error(f"The exchange rate of the date isn't available.")
        return(targetCurrency, '<NA>', '<NA>', '<NA>')

    dfs = pd.read_html(base_url+param_url+theDate)
    for i in range(0,len(dfs)-1):
        if dfs[i].iloc[0]['Currency'] == targetCurrency:
            logger.debug('Currency', dfs[i].iloc[0]['Currency'])
            tts = dfs[i].iloc[0]['TTS']
            ttb = dfs[i].iloc[0]['TTB']
            # 11:00AMまでは、ページができていてもデータがない場合がある。
            if tts == '-' and ttb == '-':
                logger.error(f"The {targetCurrency} of the date {theDate} isn't ready.")
                return targetCurrency, '<NA>', '<NA>', '<NA>'
            ttm = (float(tts) + float(ttb)) / 2
            ttm = str(f'{ttm:.2f}') # TTM treat as string for unavailable value
            return(targetCurrency, float(tts), float(ttm), float(ttb))
    logger.error(f"The {targetCurrency} could not be found.")
    return 'empty', '<NA>', '<NA>', '<NA>'

if __name__ == "__main__":
    # Please modify below listOfDate for your test
    listOfDate = ["2023/01/20", "2023/02/17", "2023/03/17", "2023/04/14", "2023/06/16", "2023/9/15", "2023/12/15"]
    targetCurrency = 'US Dollar'
    print('Target Currently: ', targetCurrency)
    print(f'date      \tTTS\tTTM\tTTB')
    for theDate in listOfDate:
        (theCurrency, tts, ttm, ttb) = getHistoricalCurrency(targetCurrency, theDate)
        print(f'{theDate}\t{tts}\t{ttm}\t{ttb}')
