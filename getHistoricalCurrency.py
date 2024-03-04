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
    # Modify below date list for the test
    #listOfDate = ["2023/2/10","2023/5/26","2023/8/10", "2023/1/19", "2023/2/15", "2023/2/18", "2023/3/17", "2023/4/13", "2023/5/6", "2023/7/7", "2023/8/4","2023/9/12"]
    #listOfDate = ["2023/10/28","2023/01/06","2023/01/06","2023/01/06","2023/01/11","2023/01/13","2023/01/13","2023/01/13","2023/01/13","2023/01/19","2023/01/20","2023/01/20","2023/01/20","2023/01/24","2023/01/27","2023/01/27","2023/01/27","2023/02/02","2023/02/03","2023/02/03","2023/02/03","2023/02/07","2023/02/07","2023/02/08","2023/02/08","2023/02/10","2023/02/10","2023/02/10","2023/02/14","2023/02/15","2023/02/16","2023/02/16","2023/02/16","2023/02/17","2023/02/17","2023/02/17","2023/02/18","2023/02/21","2023/02/24","2023/02/24","2023/02/24","2023/03/03","2023/03/03","2023/03/03","2023/03/07","2023/03/08","2023/03/08","2023/03/08","2023/03/10","2023/03/10","2023/03/10","2023/03/11","2023/03/11","2023/03/17","2023/03/17","2023/03/17","2023/03/17","2023/03/18","2023/03/24","2023/03/24","2023/03/24","2023/03/24","2023/03/29","2023/03/31","2023/03/31","2023/03/31","2023/03/31","2023/04/04","2023/04/07","2023/04/07","2023/04/07","2023/04/07","2023/04/08","2023/04/08","2023/04/11","2023/04/13","2023/04/14","2023/04/14","2023/04/14","2023/04/15","2023/04/15","2023/04/19","2023/04/21","2023/04/21","2023/04/21","2023/04/21","2023/04/21","2023/04/28","2023/04/28","2023/04/28","2023/05/06","2023/05/06","2023/05/06","2023/05/06","2023/05/06","2023/05/09","2023/05/09","2023/05/11","2023/05/12","2023/05/12","2023/05/12","2023/05/13","2023/05/17","2023/05/19","2023/05/19","2023/05/19","2023/05/26","2023/05/26","2023/05/26","2023/06/02","2023/06/02","2023/06/02","2023/06/02","2023/06/02","2023/06/07","2023/06/07","2023/06/08","2023/06/08","2023/06/09","2023/06/09","2023/06/09","2023/06/13","2023/06/13","2023/06/16","2023/06/16","2023/06/16","2023/06/16","2023/06/23","2023/06/23","2023/06/23","2023/06/24","2023/06/30","2023/06/30","2023/06/30","2023/07/04","2023/07/07","2023/07/07","2023/07/07","2023/07/07","2023/07/07","2023/07/11","2023/07/11","2023/07/14","2023/07/14","2023/07/14","2023/07/21","2023/07/21","2023/07/21","2023/07/28","2023/07/28","2023/07/28","2023/08/01","2023/08/02","2023/08/03","2023/08/04","2023/08/04","2023/08/04","2023/08/04","2023/08/05","2023/08/08","2023/08/08","2023/08/09","2023/08/12","2023/08/12","2023/08/12","2023/08/12","2023/08/16","2023/08/17","2023/08/18","2023/08/18","2023/08/18","2023/08/25","2023/08/25","2023/08/25","2023/09/01","2023/09/01","2023/09/01","2023/09/05","2023/09/07","2023/09/07","2023/09/08","2023/09/08","2023/09/08","2023/09/08","2023/09/09","2023/09/09","2023/09/12","2023/09/13","2023/09/15","2023/09/15","2023/09/15"]
    #listOfDate = ["2023/02/13"]
    #listOfDate = ["2023/02/16", "2023/05/18", "2023/08/17", "2023/11/16"]
    listOfDate = ["2023/01/20", "2023/02/17", "2023/03/17", "2023/04/14", "2023/06/16", "2023/9/15", "2023/12/15"]
    targetCurrency = 'US Dollar'
    print('Target Currently: ', targetCurrency)
    print(f'date      \tTTS\tTTM\tTTB')
    for theDate in listOfDate:
        (theCurrency, tts, ttm, ttb) = getHistoricalCurrency(targetCurrency, theDate)
        print(f'{theDate}\t{tts}\t{ttm}\t{ttb}')
