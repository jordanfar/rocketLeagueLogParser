import pickle, configparser, os

class RankPoint:

     def __init__(self, rankPointsString, dateString):
         modes = {0:'Unranked', 10:'1v1', 11:'2v2', 12:'3v3 solo', 13:'3v3'}

         self.Playlist = 0
         self.Mu = 0
         self.Sigma = 0
         self.DeltaRankPoints = 0
         self.PreRankPoints = 0
         self.Rank = 0
         self.TrueSkill = 0
         self.HumanReadablePlaylist = 'Unranked'
         self.Date = dateString

         for subString in rankPointsString.split():
             pair = subString.split("=")
             if pair[0] == 'Playlist':
                 self.Playlist= int(pair[1])
             elif pair[0] == 'Mu':
                 self.Mu = float(pair[1])
             elif pair[0] == 'Sigma':
                 self.Sigma = float(pair[1])
             elif pair[0] == 'DeltaRankPoints':
                 self.DeltaRankPoints = float(pair[1])
             elif pair[0] == 'RankPoints':
                 self.PreRankPoints = float(pair[1])

         self.Rank = self.PreRankPoints + self.DeltaRankPoints
         self.TrueSkill = round(self.Mu - 3 * self.Sigma, 8)
         self.HumanReadablePlaylist = modes[self.Playlist]

     def __eq__(self, other):
         return self.__dict__ == other.__dict__

def getHistoryData(fileName):
    """get array of RankPoint objects from history file"""
    try:
        histFile = open(fileName,"rb")
        histRP = pickle.load(histFile)
        histFile.close()
        print('Load data from {0}'.format(fileName))
        return histRP
    except:
        print('{0} does not exist'.format(fileName))
        return []

def getLogData(fileName):
    """parse logfile and return array of RankPoint objects"""
    fileName = "Launch.log"
    try:
        textFile = open(fileName, mode='r', encoding = 'ISO-8859-1')
        print ('Load data from {0}'.format(fileName))
    except:
        print('Unable to open Launch.log, ensure this program is in the same folder')
        input('Press Enter to exit')
        return None
    
    rpArray = []

    for row in textFile:
        row = row.rstrip('\n')
        if "Log file open" in row:
            date = row.split(",")[1].strip()
        elif "Log file closed" in row:
            date = row.split(",")[1].strip()
        elif "RankPoints: ClientSetSkill" in row:
            rp = RankPoint(row, date)
            rpArray.append(rp)
    return rpArray

def writeDatFile(rpArray, fileName):
    """pickle array of RankPoint objects"""
    print('Writing to {0}'.format(fileName))
    histFile = open(fileName, 'wb')
    pickle.dump(rpArray, histFile)
    histFile.close()

def prettyPrint(histRP):
    """print table of most recent match results given an array of RankPoint objects"""
    modeAndRP = {'1v1':None, '2v2':None, '3v3 solo':None, '3v3':None}
    for rp in histRP:
        if rp.HumanReadablePlaylist != 'Unranked':
            modeAndRP[rp.HumanReadablePlaylist] = rp
        
    for key, rp in sorted(modeAndRP.items()):
        if rp is None:
            print()
            print(key)
            prettyPrintRP('-', '-', '-', '-')
        else:
            print()
            print(key)
            prettyPrintRP(rp.Mu, rp.Sigma, rp.TrueSkill, rp.Rank)
    print()

def prettyPrintRP(mu, sigma, trueSkill, rankPoints):
    prettyPrintLine('Mu:', mu)
    prettyPrintLine('Sigma:', sigma)
    prettyPrintLine('TrueSkill:', trueSkill)
    prettyPrintLine('RankPoints:', rankPoints)

def prettyPrintLine(label, value):
    print('{0:13}{val}'.format(label, val=value))

def writeToCSV(histRP, fileName):
    """write RankPoints array to csv file"""
    print("Writing to {0}".format(fileName))
    csvFile = open(fileName, 'w')
    csvFile.write('Date,Playlist,Mu,Sigma,TrueSkill,RankPoints\n')
    for rp in histRP:
        line = '{0},{1},{2:.4f},{3:.4f},{4:.4f},{5:.1f}\n'.format(
            rp.Date,
            rp.HumanReadablePlaylist,
            rp.Mu,
            rp.Sigma,
            rp.TrueSkill,
            rp.Rank)
        csvFile.write(line)
    csvFile.close()

def newConfig():
     config = configparser.ConfigParser()
     config.add_section('FilePaths')
     userPath = os.path.expanduser('~')
     config.set('FilePaths', 'LogsPath', userPath +
                '/My Games/Rocket League/TAGame/Logs/')
     config.set('FilePaths', 'csv', '%(LogsPath)s/history.csv')
     config.set('FilePaths', 'dat', '%(LogsPath)s/history.dat')
     config.set('FilePaths', 'log', '%(LogsPath)s/Launch.log')
     with open('config.cfg', 'w') as configFile:
          config.write(configFile)
  
def main():
    histFileName = 'history.dat'
    logFileName = 'Launch.log'
    csvFileName = 'history.csv'

    #get an array of RankPoint objects from logfile
    logRP = getLogData(logFileName)
    if logRP is None:
        return None

    #load array of RankPoint objects from history file
    histRP = getHistoryData(histFileName)

    #combine arrays and pickle results
    if histRP == []:
        writeDatFile(logRP, histFileName)
        histRP = logRP
    else:
        if not(histRP[-1] == logRP[-1]):
            histRP += logRP
            writeDatFile(histRP, histFileName)

    #print results of most recent matches to console
    prettyPrint(histRP)
    
    #write all rankPoint objects to csv
    writeToCSV(histRP, csvFileName)


if __name__ == "__main__":
    main()
