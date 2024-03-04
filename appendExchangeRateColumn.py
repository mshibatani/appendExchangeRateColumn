#!/user/bin/python3
# Append an exchange rate column into csv file as the date filed that is defined in DATE_COLUMN_NAMES column below.
# ・CSVファイルを入力し、以下で定義されているDATE_COLUMN_NAMES列の日時の為替レートを追加し_out.csvファイルとして出力します。
# ・CSVファイルは自動判別されますが、うまくいかない場合は、SHIFT_JISとしています。
# ・日本語の日時フォーマットはxx年xx月xx日を入力できます。
# ・日本時間で取引日のない日時を入力した場合は、<NA>となります(getHistoricalCurrency.py参照)
# ・為替レートは、UFJ銀行から得ています。一度入力した日時はキャッシュされWebアクセスを軽減します。

import pandas as pd
from pandas import DataFrame
import datetime
import chardet

# Import modules advancing from logginng
from getHistoricalCurrency import getHistoricalCurrency
import progressBarWindow as pbw

# Global setup logging level for modules
import logging
logging.basicConfig()
logging.getLogger("getHistoricalCurrency").setLevel(level=logging.INFO)
logging.getLogger("progressBarWindow").setLevel(level=logging.INFO)

# Logging myself
logger = logging.getLogger(__name__)
#logger.setLevel(level=logging.DEBUG)
logger.setLevel(level=logging.INFO)

DATE_COLUMN_NAMES = ('入出金日', '国内約定日', '約定日時', '日付', 'Date')
RATE_TTM = 0
RATE_TTS = 1
RATE_TTB = 2
MAX_SKIPTRIAL = 20

#
# 日本語フォーマットの日付をdatetimeに変換
#
def jp2date(x):
    #return datetime.datetime.strptime(x, '%Y-%m-%d')
    return datetime.datetime.strptime(x, '%Y年%m月%d日')

def checkEncording(theFilePath):
    with open(theFilePath, 'rb') as f:
        c = f.read()
        result = chardet.detect(c)
        logger.debug(f"Detected the file encording: {result['encoding']}")
        return(result['encoding'])

def openPandasCSVfile(theFileName) -> DataFrame:        
    dfs = None
    theFileEncording = checkEncording(theFileName)
    if theFileEncording == None:
        theFileEncording = 'SHIFT_JIS' # as default encording
        logger.error(f"Failed to detect encording, trying to apply {theFileEncording} by force...")
    foundDateColumn = False
    for skipTrial in range(0,MAX_SKIPTRIAL):
        for dateColumnName in DATE_COLUMN_NAMES:
            try:
                dfs = pd.read_csv(theFileName, skiprows=skipTrial, index_col=dateColumnName, parse_dates=True, encoding=theFileEncording) # , index_col='日付' ,,
            except Exception as e:
                pass
                #logger.debug(f"skip:{skipTrial} {e}")
            else:
                foundDateColumn = True
                logger.debug(f"Found date format: {dateColumnName} at skip {skipTrial}")
                break
        if foundDateColumn:
            break

    if foundDateColumn:
        assert isinstance(dfs, pd.DataFrame), "dfs should be a DataFrame instance"
        checkFirstDate = str(dfs.index[0])
        if "年" in checkFirstDate and "月" in checkFirstDate and "日" in checkFirstDate:
            logger.debug("Found '年月日' thus, applying date_parser")
            dfs = pd.read_csv(theFileName, skiprows=skipTrial, index_col=dateColumnName, parse_dates=True, encoding=theFileEncording, date_parser=jp2date)
    else:
        if skipTrial == MAX_SKIPTRIAL:
            logger.error("Failed to find columns (date or encordings)")
            return None

    return dfs

#
# 取引日の為替レートカラムを追加する
#
def appendExchangeRateColumn(theFileName, theKindOfRate, progressFunc = None):

    dfs = openPandasCSVfile(theFileName)
    maxProgress = len(dfs.index)
    logger.debug(f"maxProgress: {maxProgress}")
    for i, idx in enumerate(dfs.index):
        theDate = str(idx)[0:10].replace('-','/')
        (theCurrency, tts, ttm, ttb) = getHistoricalCurrency('US Dollar', theDate)
        logger.debug(f"got TTM {ttm} for {theDate}")
        if theKindOfRate == RATE_TTB:
            dfs.loc[idx, '為替レート(TTB)'] = ttb
        elif theKindOfRate == RATE_TTS:
            dfs.loc[idx, '為替レート(TTS)'] = tts
        else: # as default behavior
            #dfs['為替レート'][index] = ttm # this makes storage warrning!!!
            dfs.loc[idx, '為替レート(TTM)'] = ttm
        if progressFunc:
            if not progressFunc(int((i/maxProgress)*100)):
                return False

    outputFilename = theFileName.replace('.csv', '_out.csv')
    logger.info(f"Creating {outputFilename}")
    dfs.to_csv(outputFilename)
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        # Confirmed detected file
        #filename = './yakujo2022.csv'
        #filename = './nyushukkin2020.csv'
        #filename = './SBI銀行_nyushukinmeisai_2022.csv'
        #filename = './yakujo2023-1.csv'
        #
        #
        # Usage:
        #   python3 ./appendExchangeRateColumn.py <filename>
        appendExchangeRateColumn(filename, RATE_TTM)
    else:
        FONT_STYLE = "any 14"
        import PySimpleGUI as sg
        sg.theme('Default')
        def fileDialogWithTT():
            #targetFile = sg.popup_get_file("Please choose a csv file", font=FONT_STYLE, file_types=(("CSV files", "*.csv"),))
            layout = [
                [sg.Text("Choose CSV file"), 
                sg.InputText(), 
                sg.FileBrowse(key="file1", file_types=(("CSV files", "*.csv"), ))], 
                [sg.Radio('TTS', key='tts', group_id='group1'), sg.Radio('TTM', default = True, key='ttm', group_id='group1'), sg.Radio('TTB', key='ttb', group_id='group1')],
                [sg.Submit(), sg.Cancel()]]
            fdWindow = sg.Window('File', layout, font=FONT_STYLE)
            event, values = fdWindow.read()
            logger.debug(f"event: {event} values: {values}")
            fdWindow.close()
            return(event, values)    

        def messageDialog(title = 'title', message='msg', button='OK'):
            layout = [[sg.Text(message)], [sg.Button(button)]]
            msgWindow = sg.Window(title, layout, font=FONT_STYLE)
            event, values = msgWindow.read()
            msgWindow.close()
            return(event, values)

        # Dialog operation: File select and choose a job radio button
        event, values = fileDialogWithTT()
        logger.debug(f"event: {event} values: {values}")
        targetFile = values['file1']
        if event == 'Submit' and targetFile:
            targetRate = RATE_TTM # as default
            if values['tts']:
                targetRate = RATE_TTS
            elif values['ttb']:
                targetRate = RATE_TTB
            
            pbw.openProgressWindow('Appending exchange rate column...')
            if not appendExchangeRateColumn(targetFile, targetRate, pbw.updateProgressWindow):
                pbw.closeProgressWindow()
                logger.info("Intentional termination")
                import sys
                sys.exit()
            pbw.closeProgressWindow()
            
            # Completed dialogue
            messageDialog(title = 'Status', message="The conversion has been completed!", button='Done')
        else:
            logger.info("Canceled")