# -*- coding: utf-8 -*-

import optparse
from probe import HProbe

def probe_url(options, videourl):
    if options.b_qp is True:
        listQP = HProbe.get_qp(videourl, skip_frame=options.skip_frame, duration_sec=options.duration)
        HProbe.print_qp(listQP)
        if options.b_nodraw is False:
            HProbe.draw_qp(listQP)

    if options.b_ci is True:
        ci = HProbe.get_coreinfo(videourl)
        HProbe.print_coreinfo(ci)

    if options.b_ts is True or options.b_vtype is True:
        fi_opts = list()
        if options.b_ts:
            fi_opts.append('ts')
        if options.b_vtype:
            fi_opts.append('pict_type')
        dictFrameInfo = HProbe.get_frameinfo(videourl, fi_opts, duration_sec=options.duration)

    if options.b_ts is True:
        HProbe.print_ts(dictFrameInfo)
        if options.b_nodraw is False:
            HProbe.draw_frame_ts(dictFrameInfo)

    if options.b_vtype is True:
        HProbe.print_vtype(dictFrameInfo)
        if options.b_nodraw is False:
            HProbe.draw_frame_vtype(dictFrameInfo)

def main():
    print("probe.py : format and visualize ffprobe's output \n"
          "Help: python3 main.py -h\n")
    parse = optparse.OptionParser(usage='"usage:%prog [options] videoURL"', version="%prog 1.0")
    # parse.add_option('-q', '--qp', dest='user', action='store', type=str, metavar='user', help='Enter User Name!!')
    parse.add_option('--qp', dest='b_qp', action='store_true', default=False, help="show video QP")
    parse.add_option('--skip_frame', action='store', dest='skip_frame', type='string', default="default",
                     help="which frame will be skip when count QP, legal value: none, default, noref, bidir, nokey, nointra, all")
    parse.add_option('--coreinfo', dest='b_ci', action='store_true', default=False, help="show core info of videoURL")
    parse.add_option('--ts', dest='b_ts', action='store_true', default=False, help="show timestamp")
    parse.add_option('--vtype', dest='b_vtype', action='store_true', default=False, help="show video frame type[IPB]")
    parse.add_option('--nodraw', dest='b_nodraw', action='store_true', default=False,
                     help="don't draw figure")
    parse.add_option('--duration', dest='duration', type='int', default=4, help="probe duration (second)")
    options, args = parse.parse_args()
    if (len(args) == 0):
        return
    probe_url(options, args[0])

if __name__ == "__main__":
    main()
