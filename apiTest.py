from ftplib import FTP
import datetime
import os

satName = ["gsat0207", "gsat0215"]
startDate = datetime.datetime(2024, 1, 16)
endDate = datetime.datetime(2024, 1, 23)
lenDays = (endDate - startDate).days + 1
datesReq = [startDate + datetime.timedelta(day) for day in range(lenDays)]

outDirBase = "/Users/matlang/PycharmProjects/galileoDataDownload/"
# for sn in satName:
#     dirNm = os.path.join(outDirBase, sn)
#     if not os.path.isdir(dirNm):
#         os.makedirs(dirNm)

fileNameBase = "galileo_gssc_emu_"
fileNameMid = "_sd_l1_"
fileNameEnd = "_V01.cdf.gz"

with FTP("gssc.esa.int", user="gssc_user_galileo", passwd="Q=`Mb>}yC=%De2<>") as ftp:
    for sn in satName:
        dirLocBase = f"/emu/galileo_gssc_emu_{sn}_sd_l1/"
        for dat in datesReq:
            print(f"{sn}: {dat}")
            yearReq = str(dat.year)
            outputDir = os.path.join(outDirBase, sn, yearReq)
            if not os.path.isdir(os.path.join(outputDir)):
                os.makedirs(os.path.join(outputDir))

            dateStr = dat.strftime("%Y%m%d")
            fToDown = f"{fileNameBase}{sn}{fileNameMid}{dateStr}{fileNameEnd}"

            # Move to required directory in ftp
            print(f"{dirLocBase}{yearReq}/")

            try:
                ftp.cwd(f"{dirLocBase}{yearReq}/")

                with open(f"{os.path.join(outputDir)}/{fToDown}", "wb") as f:
                    try:
                        ftp.retrbinary("RETR %s" % fToDown, f.write)
                    except:
                        print(f"File {fToDown} not found.")
            except:
                print(f"Directory {dirLocBase}{yearReq}/ not found.")
