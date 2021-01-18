from __future__ import print_function
import pandas as pd
import threading
from datetime import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SHEETS_ID = '1gow4eJjbJoRId6oPUsdPwDWC6y4P5WPXSPczY3kdPdY'
REALTIME_DATA = 'Realtime!A1:ZZ1000'
TRACKER_DATA = 'Tracker!A1:ZZ1000'


def equalize():
    currentRealtimeInfo = readInSheets(REALTIME_DATA)
    writeToOutput(TRACKER_DATA, currentRealtimeInfo)

def runOnce():
    minutes = 0.5
    seconds = 60.0

    currentRealtimeInfo = readInSheets(REALTIME_DATA)
    currentTrackerInfo = readInSheets(TRACKER_DATA)

    # outputTrackerData = currentTrackerInfo
    # writeToOutput(TRACKER_DATA, outputTrackerData)

    for x in range(len(currentRealtimeInfo)):
        if len(currentRealtimeInfo[x]) == 4:
            crystalBall = currentRealtimeInfo[x][3]
            if crystalBall:
                length = len(currentTrackerInfo[x])
                if currentTrackerInfo[x][length-1] != crystalBall:
                    currentTrackerInfo[x].append(currentRealtimeInfo[x][2])
                    currentTrackerInfo[x].append(currentRealtimeInfo[x][3])

    
    writeToOutput(TRACKER_DATA, currentTrackerInfo)

    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

    print("Updated: ", dt_string)
    #Loop that Shit
    # threading.Timer(minutes * seconds, runLoop).start()

def main():
    # equalize()

    print("Press Ctrl+C to exit")
    runOnce()



# --------------------------- Helpers -----------------------------------

def writeToOutput(rangeInfo, sheetData):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEETS_ID,
                                range=rangeInfo).execute()


    output = sheet.values().update(
        spreadsheetId=SHEETS_ID,
        valueInputOption='RAW',
        range=TRACKER_DATA,
        body=dict(majorDimension='ROWS', values=sheetData)
    ).execute()


def readInSheets(rangeInfo):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEETS_ID,
                                range=rangeInfo).execute()


    # Reads in the data                    
    values = result.get('values', [])

    return values

if __name__ == '__main__':
    main()