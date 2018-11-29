#
# Main core file for auto-dj
# This will handle order of operations

# import

import os
from aubio import source, tempo
from numpy import median, diff
from threading import *

# init

fileCount = 0
fileName = []
tracks = []
filePath = ""
BPMlist = []
threadCount = 0
threadCountFinished = 0
finishedThreads = []
closestBPM = []

tracksToMerge = []
linkedTracks = []


# classes

class track:

    def __init__(self, path, bpm, trackScores, pairedTracks):

        self.path = path
        self.bpm = bpm
        self.trackScores = trackScores
        self.pairedTracks = pairedTracks

    def returnBPM(self):

        return(self.bpm)

    def returnPath(self):

        return(self.path)

    def returnScores(self):

        return(self.trackScores)

    def returnTracks(self):

        return(self.pairedTracks)


# modules

def auto_dj():

    print(" auto-dj is a program that will analyse provided music in a directory and create a mix using the provided tracks. ")

    directory = input(" Please enter a single file location in which the tracks you would like mixed are stored: ")
    open_files(directory)
    threadCount = len(fileName)
    analyze_files(directory, fileName)
    print("")
    print(threadCount, " threads are currently active.")
    print("")

    while True:

        threadCountFinished = len(finishedThreads)

        if threadCountFinished == threadCount:

            print("")
            create_track_objects(BPMlist)
            find_close_bpms(tracks)
            break

    #   order_tracks(closeBPMTracks)


def open_files(directory):

    try:

        # read directory and ascertain amount of files inside, and the names of the files

        for file in os.listdir(directory):

            if file[-4:len(file)] == ".mp3":

                if os.path.isdir(file) == False:

                    fileName.append(file)

                else:

                    print("miss2")

            else:

                print("")
                print("Incompatible file: ", file,)
                print("Please check that all audio files are in the .mp3 format")

    except:

        print(":::: FAILED TO READ DIRECTORY ::::")
        print(" Please try again ")


def analyze_files(directory, fileName):

    try:

        #  launch threads equal to amount in fileCount, each thread run aubio audio analysis on the files in the directory

        # adding each individual file with the full path to a list in order to make it easier to grab the correct files later

        for file in fileName:

            if directory[-1] == "/":

                filePath = directory + file

            elif directory[-1] != "/":

                filePath = directory + "/" + file

            # creating threads for the beat detections

            print("")
            print("Currently reading file: ", file)
            threadProcessing = Thread(target=get_file_bpm, args=(filePath,))
            threadProcessing.start()

    except:

        print("Couldn't start threads.")


def get_file_bpm(filePath):

        # set the inputs up for the Aubio onset beat detection

        samplerate, win_s, hop_s = 44100, 1024, 512
        s = source(filePath, samplerate, hop_s)
        samplerate = s.samplerate
        o = tempo("specdiff", win_s, hop_s, samplerate)
        beats = []
        total_frames = 0

        # count up the beats in the track

        while True:

            samples, read = s()
            is_beat = o(samples)

            if is_beat:

                this_beat = o.get_last_s()
                beats.append(this_beat)
            total_frames += read

            if read < hop_s:
                break

        # calculate the BPM of the tracks

        if len(beats) > 1:

            if len(beats) < 4:

                print("Few beats found in ", filePath)
            BPM = 60. / diff(beats)
            trackBPM = median(BPM)

            # create a list with the tracks and their BPM

            BPMlist.append([])
            BPMlist[-1].append(filePath)
            BPMlist[-1].append(int(round(trackBPM)))
            print(BPMlist[-1])
            finishedThreads.append(len(finishedThreads))

        else:

            print("Not enough beats found in ", filePath)
            return 0


def create_track_objects(BPMlist):

    for i in range(len(BPMlist)):

        tracks.append("track" + str(i + 1))

    for i in range(len(BPMlist)):

        tracks[i] = track(BPMlist[i][0], BPMlist[i][1], [], [])

    tracks.sort(key=lambda x: x.bpm)

    #print(tracks)
    print("")


# NEED TO REWORK find_close_bpms TO USE tracks INSTEAD OF BPMlist

def find_close_bpms(tracks):

    #  add to the track objects so they hold the differences between track BPM

    for i in range(len(tracks)):

        #tracks[i].trackScores.append(tracks[i])

        for x in range(len(tracks)):

            #closestBPM[-1].append(tracks[i].bpm - tracks[x].bpm)
            #closestBPM[-1].append(round((tracks[i].bpm - tracks[x].bpm) / tracks[i].bpm * 100))

            tracks[i].trackScores.append([])
            tracks[i].trackScores[-1].append(tracks[x])

                # difference between track bpm

            #tracks[i].trackScores[-1].append(tracks[i].bpm - tracks[x].bpm)

                # % rating between track bpm

            tracks[i].trackScores[-1].append(round((tracks[i].bpm - tracks[x].bpm) / tracks[i].bpm * 100))

    for i in range(len(tracks)):

        # change the difference of a track when it is compared to itself to 999

        #print(tracks[i])
        tracks[i].trackScores[i][-1] = 999
        #print(tracks[i].trackScores)

        for x in range(len(tracks[i].trackScores)):

            if tracks[i].trackScores[x][-1] < 0:

                # multiply any number that is smaller than 0 by -1 in order to remove negatives

                #print("T")
                #print(tracks[i].trackScores[x][-1])

                noNegatives = tracks[i].trackScores[x][-1]
                noNegatives *= -1
                tracks[i].trackScores[x][-1] = noNegatives

        print(tracks[i].trackScores)
    print("")
    print(tracks)

    #print(tracks[i])
    #print(tracks[i].trackScores)

        # create a list of tracks that are close to each other and include difference

        #    lowestDiff = min(closestBPM[i])
        #    closeBPMTracks.append([])
        #    closeBPMTracks[-1].append(i)
        #    closeBPMTracks[-1].append(closestBPM[i].index(lowestDiff))
        #    closeBPMTracks[-1].append(lowestDiff)

    print("")
    print(closestBPM)


def order_tracks(closeBPMTracks):

    # check which tracks should be linked and determine which ones are connected to each other

    for i in range(len(closeBPMTracks)):

        print('track ', i)
        linkedTracks.append([])

        for x in range(len(closeBPMTracks)):

            if closeBPMTracks[x][1] == i:

                print('i ', i)
                print('x ', x)
                linkedTracks[-1].append(x)

    print(linkedTracks)

    # check all tracks have at least one pairing, maximum two pairings


    #try:

        #print(filePath)
        #aubio.source(filePath)

    #except:

        #print("Unable to process file at: ", filePath)



auto_dj()