from ij import IJ, Macro
import java.lang.Thread as Thread
# from ij.gui import WaitForUserDialog
import glob, os

__author__ = 'Nichole Wespe'

inputDir = IJ.getDirectory("Choose Source Directory ")
outputDir = IJ.getDirectory("Choose Destination Directory ")
pattern = os.path.join(inputDir, "*Start.jpg")
fileList = glob.glob(pattern)
print "Found " + str(len(fileList)) + " sample files to montage."

subDir = os.path.join(outputDir, "Montages")
if not os.path.exists(subDir):
    os.mkdir(subDir)

for f in fileList: # get date, sample from filename before opening
    date, sample, time = os.path.basename(f).split(" ")
    # find matching End.tif file
    f2 = os.path.join(inputDir, str(date) +" "+ str(sample) +" End.jpg")
    montage_name = " ".join([date, sample, "Montage.jpg"])
    path = os.path.join(subDir, montage_name)
    args = "sample=["+montage_name +"] file1=["+ f +"] file2=["+ f2 +"] path=["+ path +"]"
    Macro.setOptions(Thread.currentThread(), args)
    IJ.run("create horiz montage", args)
