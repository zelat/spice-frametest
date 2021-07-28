# 什么是帧数or帧率？
每秒的帧数(fps)或者说帧率表示图形处理器处理场时每秒钟能够更新的次数。高的帧率可以得到更流畅、更逼真的动画。一般来说30fps就是可以接受的，但是将性能提升至60fps则可以明显提升交互感和逼真感，但是一般来说超过75fps一般就不容易察觉到有明显的流畅度提升了。如果帧率超过屏幕刷新率只会浪费图形处理的能力，因为监视器不能以这么快的速度更新，这样超过刷新率的帧率就浪费掉了。

# 什么是Spice协议？
Spice 是一个开放的远程计算解决方案，使得客户端可以访问远程机器桌面和设备（比如键盘，鼠标，audio和USB）。通过Spice我们可以像使用本地计算机一样访问远程机器，这样可以把CPU GPU密集工作从客户端移交给远程高性能机器。

# 怎么测试spice的帧率？
当我们通过客户端使用远程虚拟主机的时候，通过Spice协议回传回来的数据流通过本地的图形化软件和算法形成了一个个数据帧，每秒的显示刷新率就是我们经常说的FPS。所以FPS的数据和多个外部参数有关联，

影响framerate的2个因素=数据网络传输+虚拟桌面图像渲染

## Spice-FrameTest架构
![image](https://user-images.githubusercontent.com/11868129/127300601-0840e307-4324-4376-ac8f-651b5883d5b6.png)
## Spice-FrameTest代码
Github代码仓库： https://github.com/zelat/spice-frametest

## Spice-FrameTest安装
准备一个Ubuntu Desktop虚拟机
安装依赖软件
sudo apt-get -y install ffmpeg  python3-gi  libspice-client-gtk-3.0-dev python3-libvirt   libvirt-clients
git clone https://github.com/zelat/spice-frametest
Spice-FrameTest使用步骤
1. 运行Spice-FrameTest
           python3 __main__.py --connect qemu+ssh://root@<ip.address>/system<VirshHost.No>  --loglevel <Log.level>
           ip.address: 宿主机IP地址
           VirshHost.No: 虚拟机No, 使用virsh list查看
           Log.level: 日志等级，WARN/DEBUG/INFO

2. 运行一段时间后，查看结果
    关闭SpiceGTK+的窗口后，FFmpeg自动生成测试结果
![image](https://user-images.githubusercontent.com/11868129/127300665-3ff34d00-5899-494b-9d4b-2c15fc01a220.png)

# 参考资料
https://www.cnblogs.com/silvermagic/p/7666216.html
https://github.com/JonathonReinhart/spice-record/

# QA
如何显示日志？
导入环境变量，显示日志： export FFREPORT=file=/root/Desktop/spice-log/ffmpeg-$(date +%Y%m%s).log
VDI性能开销
花费的时间=应用操作打开时间+数据网络传输时间+虚拟桌面图像渲染时间
