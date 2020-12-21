# -*- coding: utf-8 -*-

import os
import json
import numpy as np
import matplotlib.pyplot as plt


MAX_DURATION = 10*24*60*60
_gProbeCmd = "ffprobe"

class CProbe(object):
    def __init__(self):
        self._strGenOption = " -v quiet -hide_banner -print_format json "

    def get_coreinfo(self, videourl):
        strOption = self._strGenOption
        strOption += " -show_format -show_streams "
        dictProbeInfo = self.video_2_dict(videourl, strOption)
        dictCoreInfo = dict()
        dictCoreInfo['format'] = dictProbeInfo['format']
        for stream in dictProbeInfo['streams']:
            dictCoreInfo[stream['codec_type']] = stream
        # print(dictCoreInfo)
        # print(dictCoreInfo['video']['profile'])
        return dictCoreInfo

    ## options : ts、pict_type
    def get_frameinfo(self, videourl, options, duration_sec=0):
        dictFrameOption = {
            'ts' : ['pkt_pts', 'pkt_pts_time', 'pkt_dts', 'pkt_dts_time'],
            'pict_type' : ['pict_type'],
            'vframe_size' : ['pkt_size', 'pkt_dts_time']
        }
        listOption = list()
        for option in options:
            listOption += dictFrameOption[option]
        strOption = self._strGenOption
        strOption += " -show_entries format:frame=media_type,%s " % ",".join(listOption)
        strOption += """ -read_intervals "%%%d" """ % (MAX_DURATION if duration_sec <= 0 else duration_sec)
        # print(strOption)
        dictProbeInfo = self.video_2_dict(videourl, strOption)
        dictFrameInfo = dict()
        if 'ts' in options:
            dictVideoTS, dictAudioTS, listAVTSInterval_time = self.probeinfo_2_timestamp(dictProbeInfo)
            dictFrameInfo['VideoTS'] = dictVideoTS
            dictFrameInfo['AudioTS'] = dictAudioTS
            dictFrameInfo['AVTSInterval_time'] = listAVTSInterval_time
        if 'pict_type' in options:
            listPictType = self.probeinfo_2_picttype(dictProbeInfo)
            dictFrameInfo['pict_type'] = listPictType
        if "vframe_size" in options:
            listVFrameSize_byFrame, listVFrameSize_byTime = self.probeinfo_2_vframesize(dictProbeInfo)
            dictFrameInfo['vframe_size_byframe'] = listVFrameSize_byFrame
            dictFrameInfo['vframe_size_bytime'] = listVFrameSize_byTime
        return dictFrameInfo

    # -show_entries format:frame=pts,pts_time
    ## skip_frame : none, default, noref, bidir, nokey, nointra, all
    def get_qp(self, videourl, skip_frame="default", duration_sec=0):
        iFactor = 20 if skip_frame in ['nokey', 'nointra'] else 1
        iDuration = duration_sec if duration_sec>0 else 4*iFactor
        strOption = self._strGenOption
        strOption += " -select_streams v -show_frames -debug pict -show_log 48 "
        strOption += """ -read_intervals "%%%d" """ % iDuration
        strOption += " -skip_frame %s " % skip_frame
        dictProbeInfo = self.video_2_dict(videourl, strOption)
        listQP = self.probeinfo_2_qp(dictProbeInfo)
        # print(listQP)
        return listQP

    def video_2_dict(self, videourl, strOption):
        strCmd = "%s %s %s " % (_gProbeCmd, strOption, videourl)
        strProbeIno = ""
        probeOut = os.popen(strCmd)
        for line in probeOut.readlines():
            strProbeIno += line
        dictProbeInfo = json.loads(strProbeIno, encoding='utf-8')
        ## for debug
        # with open("d:/workroom/testroom/probeinfo.json", "wt", encoding='utf8') as fp:
        #     fp.write(strProbeIno)
        return dictProbeInfo

    def probeinfo_2_qp(self, dictProbeInfo):
        listQP = list()
        for frame in dictProbeInfo['frames']:
            qps = list()
            if frame.get('logs', None) is None:
                continue
            for log in frame['logs']:
                message = log['message']
                pos = message.find('qp:')
                if (pos>-1 and "slice:" in message):
                    qp = int(message[pos+3:].split(" ")[0])
                    qps.append(qp)
            listQP.append(min(qps))
        return listQP

    def probeinfo_2_picttype(self, dictProbeInfo):
        listPictType = list()
        for frame in dictProbeInfo['frames']:
            if (frame['media_type'] == 'video'):
                listPictType.append(frame['pict_type'])
        return listPictType

    def probeinfo_2_vframesize(self, dictProbeInfo):
        listVFrameSize_byFrame = list()
        listVFrameSize_byTime = list()
        if dictProbeInfo.get("frames", None) is None:
            return listVFrameSize_byFrame, listVFrameSize_byTime
        time_sec = 1.0
        size_bytime = 0
        for frame in dictProbeInfo['frames']:
            if (frame['media_type'] == 'video'):
                listVFrameSize_byFrame.append(int(frame['pkt_size']))
                pkt_dts_time = round(float(frame.get("pkt_dts_time", -1)), 6)
                if pkt_dts_time<0:
                    continue
                if pkt_dts_time>time_sec:
                    listVFrameSize_byTime.append(size_bytime)
                    size_bytime = int(frame['pkt_size'])
                    time_sec += 1.0
                else:
                    size_bytime += int(frame['pkt_size'])
        if (size_bytime>0):
            listVFrameSize_byTime.append(size_bytime)
            size_bytime = 0
        return listVFrameSize_byFrame, listVFrameSize_byTime


    def probeinfo_2_timestamp(self, dictProbeInfo):
        listKey = ['pkt_pts', 'pkt_pts_time', 'pkt_dts', 'pkt_dts_time']
        dictVideoTS = dict()
        dictAudioTS = dict()
        for key in listKey:
            dictVideoTS[key] = list()
            dictAudioTS[key] = list()
        for frame in dictProbeInfo['frames']:
            # print(frame)
            for key in listKey:
                dictTS = dictVideoTS if (frame['media_type'] == 'video') else dictAudioTS
                if (frame.get(key, None) is not None):
                    dictTS[key].append(round(float(frame[key]), 6))

        listTS = [dictVideoTS, dictAudioTS]
        for TS in listTS:
            TS['dts_interval_time'] = list()
            for i, dts in enumerate(TS['pkt_dts_time']):
                if i == 0:
                    TS['dts_interval_time'].append(0.0)
                    continue
                TS['dts_interval_time'].append(round(TS['pkt_dts_time'][i] - TS['pkt_dts_time'][i-1], 6))
            # print(TS['dts_interval_time'])

        listAVTSInterval_time = list()
        fADTS_time_current = 0.0
        for frame in dictProbeInfo['frames']:
            if frame['media_type'] == 'video' and frame.get('pkt_dts_time', None) is not None:
                listAVTSInterval_time.append(round(float(frame['pkt_dts_time']) - fADTS_time_current, 6))
            if frame['media_type'] == 'audio' and frame.get('pkt_dts_time', None) is not None:
                fADTS_time_current = round(float(frame['pkt_dts_time']), 6)
        # print(listAVTSInterval_time)
        return dictVideoTS, dictAudioTS, listAVTSInterval_time

    def draw_frame_ts(self, dictFrameInfo):
        listTSFigureParam = [("video DTS interval SEC", 'video DTS', 'time sec'),
                             ('audio DTS interval SEC', 'audio DTS', 'time sec'),
                             ('AV interval SEC', 'video DTS', 'time sec')]
        listXYAxis = [(dictFrameInfo['VideoTS']['pkt_dts_time'], dictFrameInfo['VideoTS']['dts_interval_time']),
                      (dictFrameInfo['AudioTS']['pkt_dts_time'], dictFrameInfo['AudioTS']['dts_interval_time']),
                      (dictFrameInfo['VideoTS']['pkt_dts_time'], dictFrameInfo['AVTSInterval_time'])]
        # print(dictFrameInfo['VideoTS']['dts_interval_time'])
        for i, FigureParam in enumerate(listTSFigureParam):
            plt.figure(FigureParam[0])
            plt.xlabel(FigureParam[1])
            plt.ylabel(FigureParam[2])
            minlen = min(len(listXYAxis[i][1]), len(listXYAxis[i][0]))
            y_axis = np.array(listXYAxis[i][0][0:minlen])
            x_axis = np.array(listXYAxis[i][1][0:minlen])
            plt.plot(y_axis, x_axis)
        plt.show()
        return

    def draw_vframesize(self, dictFrameInfo):
        listVFrameSize_byFrame, listVFrameSize_byTime = dictFrameInfo['vframe_size_byframe'], dictFrameInfo['vframe_size_bytime']
        plt.figure("VFrame size by frame")
        plt.xlabel("Frame SN")
        plt.ylabel("VFrame size")
        y_axis0 = np.array(listVFrameSize_byFrame)
        plt.plot(y_axis0)

        plt.figure("VFrame size by time")
        plt.xlabel("time(second)")
        plt.ylabel("VFrame size")
        y_axis1 = np.array(listVFrameSize_byTime)
        plt.plot(y_axis1)
        plt.show()

    def draw_qp(self, listQP):
        plt.figure("QP")
        plt.xlabel("Frame SN")
        plt.ylabel("QP value")
        y_axis = np.array(listQP)
        plt.plot(y_axis)
        plt.show()
        return

    def draw_frame_vtype(self, dictFrameInfo):
        dictType2Num = {
            'I' : 0,
            'P' : 1,
            'B' : 2
        }
        listVType = dictFrameInfo['pict_type']
        listVType_num = list(map(lambda x : dictType2Num.get(x, -1), listVType))
        plt.figure("Frame type")
        plt.xlabel("Frame SN")
        plt.ylabel("Type")
        y_axis = np.array(listVType_num)
        x_axis = np.array(range(0, len(y_axis)))
        plt.scatter(x_axis, y_axis, c='b', alpha=0.9)
        plt.show()
        return

    def print_coreinfo(self, dictCoreInfo):
        dictFormat = dictCoreInfo['format']
        print("Format : ")
        for (k, v) in dictFormat.items():
            print("\t%s : %s" % (k, v))

        listAV = ['video', 'audio']
        for av in listAV:
            if (dictCoreInfo.get(av, None) is not None):
                print("\n%s Info :" % av.upper())
                dictVI = dictCoreInfo[av]
                for (k, v) in dictVI.items():
                    print("\t%s : %s" % (k, v))

    def print_qp(self, listQP):
        print("Video frame QP : ")
        for (i, qp) in enumerate(listQP):
            print("NO.%d : %d" % (i, qp))
        print("mean QP : %05f" % (float(sum(listQP))/len(listQP)))

    def print_vtype(self, dictFramInfo):
        listVType = dictFramInfo['pict_type']
        print("Video frame type : ")
        for (i, vtype) in enumerate(listVType):
            print("NO.%d : %s" % (i, vtype))

    def print_vframesize(self, dictFrameInfo):
        listVFrameSize_byFrame = dictFrameInfo['vframe_size_byframe']
        listVFrameSize_byTime = dictFrameInfo['vframe_size_bytime']
        print("Video frame size by frame : ")
        for (i, vfsize) in enumerate(listVFrameSize_byFrame):
            print("NO.%d\t%d" % (i, vfsize))
        print("Video frame size by time : ")
        for (i, vfsize) in enumerate(listVFrameSize_byTime):
            print("Time : %ds\t%d" % (i, vfsize))

    def print_ts(self, dictFrameInfo):
        listKey = ['pkt_pts', 'pkt_pts_time', 'pkt_dts', 'pkt_dts_time', 'dts_interval_time']
        dictVideoTS = dictFrameInfo['VideoTS']
        dictAudioTS = dictFrameInfo['AudioTS']
        listTS = [dictVideoTS, dictAudioTS]
        listAV = ['VIDEO', 'AUDIO']
        for (i, TS) in enumerate(listTS):
            print("\n%s timestamp info:" % listAV[i])
            print("%s" % "\t".join(listKey))
            minlen = min(list(map(lambda x : len(TS[x]), listKey)))
            # print(minlen)
            for ii in range(0, minlen):
                listInfo = list(map(lambda x : str(TS[x][ii]), listKey))
                print("%s" % "\t".join(listInfo))
        print("\nAV interval info:")
        print("video-dts-time\tAV-interval-time")
        for i in range(0, min(len(dictFrameInfo['AVTSInterval_time']), len(dictVideoTS['pkt_dts_time']))):
            print("%s\t%s" % (str(dictVideoTS['pkt_dts_time'][i]), str(dictFrameInfo['AVTSInterval_time'][i])))

    def print(self):
        print(_gProbeCmd)

HProbe = CProbe()


if __name__=="__main__":
    # videourl = "rtmp://14.29.108.156/zeushub/willwanghanyu1500K?domain=play-qiniu.cloudvdn.com"
    # videourl = "d:\\workroom\\testroom\\48.mp4"
    videourl = "d:\\workroom\\testroom\\40s640x360.mp4"
    HProbe.print()
    # listQP = HProbe.get_qp(videourl, skip_frame="default", duration_sec=0)
    # HProbe.draw_qp(listQP)
    # HProbe.print_qp(listQP)

    # ci = HProbe.get_coreinfo(videourl)
    # HProbe.print_coreinfo(ci)
    dictFrameInfo = HProbe.get_frameinfo(videourl, ['ts', 'pict_type', 'vframe_size'], duration_sec=30)
    # HProbe.draw_frame_ts(dictFrameInfo)
    # HProbe.draw_frame_vtype(dictFrameInfo)
    # HProbe.print_vtype(dictFrameInfo)
    # HProbe.print_ts(dictFrameInfo)
    HProbe.draw_vframesize(dictFrameInfo)
    HProbe.print_vframesize(dictFrameInfo)

