#! /usr/bin/env python3

import matplotlib.pyplot as plt
import mplcursors
from adjustText import adjust_text
import json
import collections
import os
import sys
import pandas as pd

from numpy import true_divide

# 6 black
plt_color=["blue", "red", "green", "cyan", "magenta", "yellow", "black"]

class perfBreak():
    def __init__(self, func, ppid, pid, tid, flag, time, offset, range):
        self.func = func
        self.ppid = ppid
        self.pid = pid
        self.tid = tid
        self.flag = flag
        self.time = time
        self.offset = offset
        self.range = range

class perfNotes():
    def __init__(self, pid, tid, y, left, color, alpha, text, ycount):
        self.pid = pid
        self.tid = tid
        self.y = y
        self.left = left
        self.color = color
        self.alpha = alpha
        self.text = text
        self.ycount = ycount

class perfCursors():
    def __init__(self, tid, y, text, time, offset, color):
        self.tid = tid
        self.y = y
        self.text = text
        self.time = time
        self.offset = offset
        self.color = color


def getFront2Last (line):
    front = "perfBreak:{"
    last = "}"
    begin = line.find(front) + len(front) - 1
    word = line[begin:]
    end = word.find(last) + 1
    # print("begin=",begin,"end=",end)
    # print(word[:end])
    return word[:end]

def applyFile (file_name):
    lpoint = []
    lshow = []
    key_word = "perfBreak:"
    f_log = open(file_name,"r",encoding='utf-8')
    line_log = f_log.readline()

    while line_log:
        if key_word in line_log :
            key_val = getFront2Last(line_log)
            data = json.loads(key_val)
            lpoint.append(perfBreak(data['func'], data['ppid'], data['pid'], data['tid'], data['flag'], data['time'], 0, data['range']))
            # print("key_val=", key_val)
        line_log = f_log.readline()  #read the next line

    f_log.close()

    lpoint.sort(key=lambda x:x.time)
    diffVal = len(str(lpoint[len(lpoint) - 1].time - lpoint[0].time)) + 1
    noteCsv = {'ppid':[], 'pid':[], 'tid':[], 'func':[], 'time_start':[], 'time':[]}
    for var in range(len(lpoint)):
        if (lpoint[var].flag == 0):
            for n in range(var + 1, len(lpoint)):
                if (lpoint[n].pid == lpoint[var].pid and lpoint[n].tid == lpoint[var].tid \
                    and lpoint[n].range == lpoint[var].range and lpoint[n].flag == 0) :
                    lpoint[var].flag = 2 #Delete the single start item
                    break
                if (lpoint[n].pid == lpoint[var].pid and lpoint[n].tid == lpoint[var].tid \
                    and lpoint[n].range == lpoint[var].range and lpoint[n].flag == 1) :
                    lpoint[var].offset = lpoint[n].time - lpoint[var].time
                    lpoint[n].flag = 2
                    lshow.append(perfBreak(lpoint[var].func, lpoint[var].ppid, lpoint[var].pid, lpoint[var].tid,\
                        lpoint[var].flag, int(str(lpoint[var].time)[-diffVal:]), lpoint[var].offset, lpoint[var].range))
                    print ("lpoint:%d func:%s var.range:%s " %(n, lpoint[n].func, lpoint[var].range))
                    noteCsv["ppid"].append(lpoint[var].ppid)
                    noteCsv["pid"].append(lpoint[var].pid)
                    noteCsv["tid"].append(lpoint[var].tid)
                    noteCsv["func"].append(lpoint[var].range)
                    noteCsv["time_start"].append(int(str(lpoint[var].time)[-diffVal:]))
                    noteCsv["time"].append(lpoint[var].offset)
                    break
    # for i in lshow:
    #     print ("var['offset']: ", i.offset)
    dataframe = pd.DataFrame(noteCsv)
    dataframe.to_csv("perfBreak.csv", index=False, sep=',')
    return lshow  #sorted(lshow, key=lambda x:x.time)

if __name__ == '__main__':
    if len(sys.argv) <= 1 :
        print("Please add log eg.: ./perftool.py ./test.log")
        sys.exit(0)

    perfVal = applyFile(sys.argv[1])
    height = 0.3
    org_alpha = 0.8
    showNotes = collections.OrderedDict()
    showText = collections.OrderedDict()
    ylim = len(perfVal)
    texts = []
    debug = True

    # fig = plt.figure(figsize=((15,10)))
    fig = plt.figure()
    plot = plt.subplot(111)

    for n in range(len(perfVal)):
        if debug :
            print ("get:%d flag:%d offset:%s time:%s range: %s" %(n, perfVal[n].flag, perfVal[n].offset, perfVal[n].time, perfVal[n].range))
        if perfVal[n].flag == 0 :
            if (n == 0) :
                plot.barh(ylim, perfVal[n].offset, height=height, left=perfVal[n].time, color=plt_color[n], alpha=org_alpha)
                # texts += [plot.text(perfVal[n].time, ylim - 0.05, "%s:%d/%dms" %(perfVal[n].range, perfVal[n].time, perfVal[n].offset))]
                plt.yticks([ylim],[str(perfVal[n].tid)] )
                showNotes[perfVal[n].tid] = perfNotes(perfVal[n].pid, perfVal[n].tid, ylim, (perfVal[n].time + perfVal[n].offset), \
                    n, org_alpha, perfVal[n].range, 1)
                showText[ylim] = [perfCursors(perfVal[n].tid, ylim, perfVal[n].range, perfVal[n].time, perfVal[n].offset, n)]
                # perfCursors(self, tid, y, text, time, offset, color)
                if debug :
                    print("--->set 1: y:%d tid:%d range:%s color:%s alpha:%.2f offset:%d" \
                        %(ylim, perfVal[n].tid, perfVal[n].range, plt_color[n], org_alpha, perfVal[n].offset))
                perfVal[n].flag = 1
            elif perfVal[n].tid in showNotes :
                tmp = showNotes[perfVal[n].tid]
                # alpha = (0.2 if tmp.alpha > 0.2 else org_alpha)
                alpha = 0.2
                # if perfVal[n].time < tmp.left:
                color = 0 if tmp.color >= len(plt_color) - 2 else (tmp.color + 1)
                if (perfVal[n].time > tmp.left) :
                    plot.barh(tmp.y, (perfVal[n].time - tmp.left), height=height, left=tmp.left, color=plt_color[len(plt_color) - 1], alpha=org_alpha)
                    # texts += [plot.text(tmp.left, tmp.y - 0.05, "other: %dms" %(perfVal[n].time - tmp.left))]
                    showText[tmp.y].append(perfCursors(perfVal[n].tid, tmp.y, "other", tmp.left, (perfVal[n].time - tmp.left), (len(plt_color) - 1)))
                plot.barh(tmp.y, perfVal[n].offset, height=height, left=perfVal[n].time, color=plt_color[color], alpha=alpha)
                # texts += [plot.text(perfVal[n].time, tmp.y - 0.05, "%s:%d/%dms" %(perfVal[n].range, perfVal[n].time, perfVal[n].offset))]
                # plt.yticks([tmp.y], [perfVal[n].tid] )
                # matplotlib.pyplot.barh(y, width, height=0.8, left=None, *, align='center', **kwargs)[source]
                # (self, pid, tid, y, left, color, alpha, text)
                showNotes[perfVal[n].tid] = perfNotes(perfVal[n].pid, perfVal[n].tid, tmp.y, (perfVal[n].time + perfVal[n].offset), \
                    color, alpha, perfVal[n].range, tmp.ycount)
                showText[tmp.y].append(perfCursors(perfVal[n].tid, tmp.y, perfVal[n].range, perfVal[n].time, perfVal[n].offset, color))
                # perfCursors(self, tid, y, text, time, offset, color)
                if debug :
                    print("--->set 2: y:%d tid:%d range:%s color:%s alpha:%.2f offset:%d" \
                        %(tmp.y, perfVal[n].tid, perfVal[n].range, plt_color[color], alpha, perfVal[n].offset))
                perfVal[n].flag = 1

            else :
                tmp = showNotes[list(showNotes.keys())[-1]]
                # alpha = (0.2 if tmp.alpha > 0.2 else org_alpha)
                alpha = org_alpha
                # color = 0 if tmp.color >= len(plt_color) - 2 else (tmp.color + 1)
                color = 0
                # if perfVal[n].pid in showNotes
                y = tmp.y - 1 - ((tmp.ycount - 1) * height)
                plot.barh(y, perfVal[n].offset, height=height, left=perfVal[n].time, color=plt_color[color], alpha=alpha)
                # texts += [plot.text(perfVal[n].time, y - 0.05, "%s:%d/%dms" %(perfVal[n].range, perfVal[n].time, perfVal[n].offset))]
                plt.yticks([y], [str(perfVal[n].tid)] )
                # (self, pid, tid, y, left, color, alpha, text)
                showNotes[perfVal[n].tid] = perfNotes(perfVal[n].pid, perfVal[n].tid, y, (perfVal[n].time + perfVal[n].offset), \
                    color, alpha, perfVal[n].range, 1)
                showText[y] = [perfCursors(perfVal[n].tid, y, perfVal[n].range, perfVal[n].time, perfVal[n].offset, color)]
                if debug :
                    print("--->set 3: y:%d tid:%d range:%s color:%s alpha:%.2f offset:%d" \
                        %(y, perfVal[n].tid, perfVal[n].range, plt_color[color], alpha, perfVal[n].offset))
                perfVal[n].flag = 1

            for i in range(n + 1, len(perfVal)) :
                if perfVal[n].tid == perfVal[i].pid and perfVal[n].tid != perfVal[i].tid and perfVal[i].flag == 0 :
                    if perfVal[i].tid in showNotes :
                        tmp = showNotes[perfVal[i].tid]
                        # alpha = (0.2 if tmp.alpha > 0.2 else org_alpha)
                        alpha = org_alpha
                        # if perfVal[i].time < tmp.left:
                        color = 0 if tmp.color >= len(plt_color) - 2 else (tmp.color + 1)
                        if (perfVal[i].time > tmp.left) :
                            plot.barh(tmp.y, (perfVal[i].time - tmp.left), height=height, left=tmp.left, color=plt_color[len(plt_color) - 1], alpha=org_alpha)
                            # texts += [plot.text(tmp.left, tmp.y - 0.05, "other: %dms" %(perfVal[i].time - tmp.left))]
                            showText[tmp.y].append(perfCursors(perfVal[i].tid, tmp.y, "other", tmp.left, (perfVal[i].time - tmp.left), (len(plt_color) - 1)))
                        plot.barh(tmp.y, perfVal[i].offset, height=height, left=perfVal[i].time, color=plt_color[color], alpha=alpha)
                        # texts += [plot.text(perfVal[i].time, tmp.y - 0.05, "%s:%d/%dms" %(perfVal[i].range, perfVal[i].time, perfVal[i].offset))]
                        # plt.yticks([tmp.y], [perfVal[i].tid] )
                        # (self, pid, tid, y, left, color, alpha, text)
                        showNotes[perfVal[i].tid] = perfNotes(perfVal[i].pid, perfVal[i].tid, tmp.y, (perfVal[i].time + perfVal[i].offset), \
                            color, alpha, perfVal[i].range, tmp.ycount)
                        showText[tmp.y].append(perfCursors(perfVal[i].tid, tmp.y, perfVal[i].range, perfVal[i].time, perfVal[i].offset, color))
                        if debug :
                            print("--->set 4: y:%d tid:%d range:%s color:%s alpha:%.2f offset:%d" \
                                %(tmp.y, perfVal[i].tid, perfVal[i].range, plt_color[color], alpha, perfVal[i].offset))
                        perfVal[i].flag = 1
                    else :
                        tmp = showNotes[list(showNotes.keys())[-1]]
                        # alpha = (0.2 if tmp.alpha > 0.2 else org_alpha)
                        alpha = org_alpha
                        color = 0 if tmp.color >= len(plt_color) - 1 else (tmp.color + 1)
                        y = tmp.y - height
                        plot.barh(y, perfVal[i].offset, height=height, left=perfVal[i].time, color=plt_color[color], alpha=alpha)
                        # texts += [plot.text(perfVal[i].time, y - 0.05, "%s:%d/%dms" %(perfVal[i].range, perfVal[i].time, perfVal[i].offset))]
                        plt.yticks([y], [str(perfVal[i].tid)] )
                        # (self, pid, tid, y, left, color, alpha, text)
                        showNotes[perfVal[i].tid] = perfNotes(perfVal[i].pid, perfVal[i].tid, y, (perfVal[i].time + perfVal[i].offset), \
                            color, alpha, perfVal[i].range, tmp.ycount + 1)
                        showText[y] = [perfCursors(perfVal[i].tid, y, perfVal[i].range, perfVal[i].time, perfVal[i].offset, color)]
                        if debug :
                            print("--->set 5: y:%d tid:%d range:%s color:%s alpha:%.2f offset:%d" \
                                %(y, perfVal[i].tid, perfVal[i].range, plt_color[color], alpha, perfVal[i].offset))
                        perfVal[i].flag = 1

    y = []
    ticks = []
    for v in showNotes :
        # print("-->set 6: y %d  tid %d" %(showNotes[v].y, showNotes[v].tid))
        y += [showNotes[v].y]
        ticks += [str(showNotes[v].tid)]
        # ticks += ["%d-%d" %(showNotes[v].pid, showNotes[v].tid)]
    plt.yticks(y, ticks)

    yused = []
    for y in showText :
            step = 1
            while (y - step * height) in showText :
                step = step + 1
            # step = step - 1
            des = ""
            for var in showText[y] :
                des += "[%s:%d]"%(var.text, var.offset)
            ySet = y - step * height
            for i in yused :
                if int(i * 10) == int(ySet * 10) :
                    ySet = ySet - height
            texts += [plot.text(perfVal[0].time, (ySet - 0.05), "%s" %(des), in_layout=True)]
            yused.append(ySet)

    # perfCursors(self, tid, y, text, time, offset, color)
    # texts += [plot.text(perfVal[n].time, ylim - 0.05, "%s:%d/%dms" %(perfVal[n].range, perfVal[n].time, perfVal[n].offset))]

    # plt.xlim(perfVal[0].time, perfVal[len(perfVal) - 1].time + 1000)
    # plt.ylim(0, ylim + 3)
    plt.xlabel("Time(ms)")
    plt.ylabel('Tid')
    plt.title("Performance")

    crs = mplcursors.cursor(plot,hover=True)
    # crs.connect("add", lambda sel: sel.annotation.set_text(
    #     'Point ({:.0f},{:.1f})'.format(sel.target[0], sel.target[1])))
    def getText (x , y) :
        text = ""
        for i in showText :
            if int(y * 10) in range(int(i * 10 - 1), int(i * 10 + 1)) :
                # print("i: %f  y:%f" %(i, x))
                for n in showText[i] :
                    # print("y: %f  show: %f" %(x, n.time + n.offset))
                    if int(n.time + n.offset) == int(x) :
                        return "%s[%d,%d:%d(ms)]" %(n.text, n.time, x, n.offset)
        return ""

    crs.connect("add", lambda sel: sel.annotation.set_text(
        '{}'.format(getText(sel.target[0] , sel.target[1]))))

    # adjust_text(texts)
    # fig.canvas.draw()
    # plt.tight_layout()

    plt.savefig("perfBreak.svg", format="svg")
    # plt.savefig('perfBreak.png')
    plt.show()


