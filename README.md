# HProbe
ffprobe 输出可视化工具

## 1. 概述
*HProbe* 是一个 ffprobe 输出的可视化工具脚本， v 1.0 支持文件核心信息、视频帧类型、视频帧QP以及时间戳相关的信息打印及可视化

## 2. 例子
*查看 v_type*
```bash
python3  main.py --vtype  "rtmp://14.29.108.156/zeushub/willwanghanyu1500K?domain=play-qiniu.cloudvdn.com"
```
*查看 QP*
```bash
python3  main.py --qp --nodraw "rtmp://14.29.108.156/zeushub/willwanghanyu1500K?domain=play-qiniu.cloudvdn.com"
```
*查看 时间戳*
```bash
python3  main.py --ts "rtmp://14.29.108.156/zeushub/willwanghanyu1500K?domain=play-qiniu.cloudvdn.com"
```
*查看 文件基本信息*
```bash
python3  main.py --coreinfo "rtmp://14.29.108.156/zeushub/willwanghanyu1500K?domain=play-qiniu.cloudvdn.com"
```
*查看 视频帧尺寸
```bash
python3  main.py --vframesize "rtmp://14.29.108.156/zeushub/willwanghanyu1500K?domain=play-qiniu.cloudvdn.com"
```


## 3. 注意事项
### 建议使用 python 3 
### 请注意把 ffprobe 所在目录放入 PATH 环境变量中
### --qp 执行超级慢，请用类似命令去执行：nohup python3  main.py --qp  --nodraw --duration 1 d:\workroom\testroom\avsmart-noenh\avsmart2_2-mission-impossible-fallout-trailer-1_h1080p.mp4 > nohup.out

`--skip_frame` 只在 qp 时有效

`--duration` 默认是 **4秒**

`--vtype` 在显示时，*0* 表示 **I** 帧，*1* 表示 **P** 帧，*2* 表示 **B** 帧

## 4. 版本日志
### v 1.0.2 20201223
`
修复了 qp 的计算方法，现在不是取 slice qp 了，而是把所有 mb qp 相加求平均了
增加了 I、P、B 的统计信息
`
### v 1.0.1 20201221
`
新增支持视频帧尺寸
`
