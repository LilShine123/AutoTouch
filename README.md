# AutoTouch 自动点击器
A strong auto touch tool. 一款强大的自动点击工具

🎯 Core Operations
Add Click Point: Press the Spacebar (Global Hotkey) or click the "Add (Space)" button to create a point at the current mouse cursor position. The number label is aligned precisely with the click coordinates (no offset).

Delete Point: Select a point in the list and click "Delete Selected". The corresponding on-screen marker will disappear instantly.

Clear All: Remove all points with one click (a confirmation dialog appears to prevent accidental deletion).

Modify Repeat Count: Select a point in the list, enter a new number (≥ 1) in the "Modify Count" field, and click "Apply". This lets you set a custom repeat count for each individual point (default is 1).

⚙️ Execution Logic
Execution Order: Points are executed strictly from top to bottom (in the order they appear in the list).

Click Frequency: "Clicks per Second" controls the speed for a single point (e.g., 2 clicks/sec ≈ 0.5s interval).

Delay Between Points: "Interval Between Points (seconds)" sets the waiting time after one point finishes before moving to the next (default is 0.5s).

Loop Mode: Check "Loop" to return to the first point and repeat infinitely after finishing one cycle. Uncheck it to stop automatically after a single round.

Round Counter: The status bar displays the current round (e.g., "Round X"). When stopped, it clearly shows: "Stopped: [Reason], Total Rounds Executed: X".

🛡️ Smart Safety Features (Anti-Misoperation)
Auto-Stop on Mouse Movement: If you manually move the mouse more than 300 pixels during the clicking process, the program will automatically stop (the threshold has been increased to prevent accidental triggers between point switches).

Emergency Stop: Quickly move your mouse to the top-left corner of the screen to instantly terminate the program (native pyautogui failsafe mechanism).

Runtime Lock (Concurrency Protection): While running, the "Add", "Delete", "Clear", and "Apply" buttons are automatically disabled to prevent list modifications that could cause crashes.

Exception Handling: If a click fails (e.g., coordinates are out of the screen), the status bar will show "Click Exception (x,y): [Error Details]" to help you locate the problem quickly.

📋 On-Screen Visual Assistance
Semi-transparent Number Markers: After adding a point, a numbered yellow label will appear on the screen at the exact click position (precisely aligned, no offset).

Draggable Markers: You can drag these yellow labels with your mouse to fine-tune their positions. After releasing, the program automatically updates the coordinate data for that point (the list syncs instantly).

Real-time Mouse Position: The interface displays the current mouse coordinates in real-time, helping you preview where your next click will land.

💾 Configuration Archiving (JSON)
Save Configuration: Click the "💾 Save Config" button to export all current points (coordinates + repeat counts) to a .json file (you can name it whatever you like).

Load Configuration: Click the "📂 Load Config" button to select a previously saved .json file and restore all click points instantly—no need to re-add them manually.

⌨️ Global Hotkeys (Work Without Window Focus)
Spacebar: Add the current mouse position as a click point (works even when the program is in the background).

ESC Key: Start / Stop the clicking process (toggles the function, synchronized with the main button).

🌐 Window & UI
Always on Top: Enabled by default to keep the window above other applications; uncheck it to return to normal layering.

Layout: All controls (buttons, input fields, list) are logically arranged. The window size is fixed at 720x510, ensuring all features are fully visible without scrolling.

Help Menu: Click "📖 Help" to pop up a complete user guide, making it easy for beginners to get started.

Timer Stop: Enter minutes in the "Timer (minutes)" field and click "Timer" to start a countdown. It will automatically stop the clicking when time runs out (if not running, it will start automatically first).

🎯 核心操作功能
添加点击点：按下 空格键（全局热键） 或点击“添加 (空格)”按钮，在鼠标当前位置精准生成点（数字标签精确对齐点击坐标，无偏移）。

删除点：在列表中选择一个点，点击“删除选中”，对应的屏幕标记同步消失。

清空全部：一键清空所有点（有确认弹窗，防止误触）。

修改次数：选中列表中的点，在“修改次数”输入框输入数字（≥1），点击“应用”，即可单独设置该点的重复执行次数（默认1次）。

⚙️ 点击执行逻辑
执行顺序：严格按照列表从上到下的顺序依次执行。

单点频率：“每秒次数”控制单个点内部的点击速度（例：2次/秒 ≈ 间隔0.5秒）。

点间延迟：“点间间隔(秒)”控制上一个点执行完毕后，等待多久再执行下一个点（默认为0.5秒）。

循环模式：勾选“循环”时，执行完最后一圈自动回到第一个点无限循环；取消勾选则执行完一轮自动停止。

轮次计数：状态栏实时显示“第X轮”，停止时会清晰显示 “已停止：原因，共执行 X 轮”。

🛡️ 智能安全保障（防误触/防崩溃）
鼠标晃动自动停止：点击过程中如果鼠标被移动超过 300 像素，程序自动停止（阈值已调高，不再因点间切换误判）。

紧急停止：将鼠标快速移到屏幕左上角，程序立即终止（pyautogui原生安全机制）。

运行锁（防并发）：点击运行时，“添加”、“删除”、“清空”、“应用”按钮会被自动禁用，防止因修改列表导致程序崩溃。

异常捕获：如果点击某个坐标失败（如坐标超出屏幕），状态栏会明确显示 “点击异常（坐标x,y）：错误详情”，方便您定位问题。

📋 屏幕可视化辅助
半透明数字标记：添加点后，屏幕上会出现一个带有数字编号的半透明黄色标签（位置精准对齐鼠标点击处）。

标记可拖动：您可以用鼠标左键拖拽这些黄色标签来微调位置，松开后程序会自动更新该点的坐标数据（列表同步刷新）。

实时鼠标位置：界面右上角实时显示当前鼠标坐标，方便您预览落点。

💾 配置存档功能（JSON）
保存配置：点击“💾 保存配置”，将当前所有点（坐标 + 重复次数）保存为 .json 文件（可任意命名）。

加载配置：点击“📂 加载配置”，读取之前的 .json 文件，恢复所有点击点，省去重复添加的麻烦。

⌨️ 全局热键（无需窗口焦点）
空格键：添加当前鼠标位置为点击点（即使在后台运行也有效）。

ESC键：开始 / 停止点击（切换功能，与主界面按钮同步）。

🌐 窗口与界面
窗口置顶：默认开启“置顶”功能，防止窗口被其他应用遮挡；取消勾选即可恢复普通层级。

界面布局：所有控件（按钮、输入框、列表）合理排布，窗口大小固定为 720x510，完整显示所有功能无需滚动。

操作说明：点击“📖 操作说明”弹出完整使用指南，便于新手快速上手。

定时停止：输入分钟数，点击“定时”开始倒计时，时间到自动停止点击（若未开始则先自动开始）。


------------------------------------------------------------------------------------
Basic runtime dependencies  基础运行依赖

pip install pyautogui keyboard

It is recommended to run Python / EXE as administrator, otherwise the global hotkeys may not work in the background. 建议以管理员身份运行 Python / EXE，否则全局热键可能无法在后台生效。






