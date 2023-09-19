import os
import core
from core import isPDF, unlockPDF, savePDF

tasks = []  # paths
showlist = []  # (num, path, passwd, state)

getshownum = lambda path: [n for n,p,_,_ in showlist if p==path][0]

def checkinfilelist(lst):
    for i in sorted(set(lst)):
        i = os.path.normpath(i)
        if isPDF(i):
            tasks.append(i)
    if tasks:
        root.after(0, updatelist)
    else:
        messagebox.showwarning(mktitle('文件无效'), '没有检测到任何有效 PDF 文档！')

isnextpage = False
def nextpage():
    global isnextpage
    isnextpage = True
    mainframe.pack_forget()
    procframe.pack(fill='both', expand=True)
    root.title(mktitle('文件解锁中，可以继续放入文件'))

def askpasswd(filename):  # TODO!!!
    password = simpledialog.askstring("解密需要密码", f"请输入用于打开 “{filename}” 的密码")
    if password is not None:
        core.passwdStorage.append(password)
        return True
    else:
        return False

def updatelist():
    if not isnextpage:
        nextpage()
    root.update()
    updateTreeview()
    root.update()
    while tasks:
        path = tasks.pop()
        num = getshownum(path)
        while True:  # Unlocking current file
            result = unlockPDF(path)
            match result:
                case 'Unlocked':
                    passwd, pdf = result.more
                    savePDF(path, pdf)
                    showlist[num][2] = passwd
                    showlist[num][3] = '已完成'
                    break
                case 'NoPassword':
                    if askpasswd(os.path.basename(path)):
                        continue
                    else:
                        showlist[num][3] = '密码不正确'
                        break
                case 'Error':
                    showlist[num][3] = '意外错误'
                    showlist[num][3] = '意外错误' + str(result.more)
                    break
        renderTreeview()
        root.update()
    renderTreeview()

def updateTreeview():
    showlist_paths = [path for _,path,_,_ in showlist]
    paths_to_add = [path for path in tasks if path not in showlist_paths]
    while paths_to_add:
        path = paths_to_add.pop()
        num = showlist[-1][0] + 1 if showlist else 0
        tree.insert('', 'end', num, values=('', '', ''))
        showlist.append([num ,path, None, '等待'])
    tree.see(showlist[-1][0])
    renderTreeview()

def renderTreeview():
    for num, _ in enumerate(showlist):
        num, path, passwd, state = _
        tree.set(num, 'path', os.path.basename(path))
        if passwd:
            tree.set(num, 'passwd', passwd)
        elif passwd == '':
            tree.set(num, 'passwd', '无需密码')
        else:
            tree.set(num, 'passwd', '')
        tree.set(num, 'state', state)

def btn_openfile(_=...):
    # 打开选择文件对话框并加入列表
    files = filedialog.askopenfilenames(title='选择要解锁的 PDF 文件', filetypes=(('PDF 文档', '*.pdf'), ('所有文件', '*.*')))
    if files:
        checkinfilelist(files)

def dropHandler(event):
    # This function is called, when stuff is dropped into a widget
    def path_walker(path):
        files_list = []
        for root, dirs, files in os.walk(path):
            for f in files:
                files_list.append(os.path.join(root, f))
        return files_list
    def data_parser(data):
        data = list(data)
        li = []
        stk = []
        close = 0
        while len(data):
            n = data.pop(0)
            if n == '\\':
                stk.append(data.pop(0))
            elif n == '{':
                if close:
                    stk.append(n)
                close += 1
            elif n == '}':
                close -= 1
                if close:
                    stk.append(n)
                else:
                    if stk:
                        li.append(''.join(stk))
                        stk.clear()
            elif n == ' ' and not close:
                if stk:
                    li.append(''.join(stk))
                    stk.clear()
            else:
                stk.append(n)
        if stk:
            li.append(''.join(stk))
            stk.clear()
        return li
    targets = []
    for i in data_parser(event.data):
        if os.path.isdir(i):
            targets.extend(path_walker(i))
        else:
            targets.append(i)
    checkinfilelist(targets)

mktitle = lambda x: 'PDF 解锁酶' + ' - ' + x

def ui():
    global filedialog, messagebox, simpledialog
    import tkinter as tk
    from tkinter import ttk, filedialog, font, messagebox, simpledialog
    import tkinterDnD
    global root, mainframe, procframe, tree

    # 更改当前工作目录到脚本所在的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 创建主窗口
    root = tkinterDnD.Tk()  # Drag and drop plugin init
    root.withdraw()
    root.geometry('500x500')
    root.resizable(False, False)
    root.title(mktitle('文件拖入此窗口'))
    root.iconbitmap('icon.ico')
    root.bind("<Control-w>", lambda _: exit())
    root.bind("<Escape>", lambda _: exit())
    root.bind("<Return>", btn_openfile)

    # 设置初始量
    defaultfont = font.nametofont("TkDefaultFont").actual()["family"]
    logo = tk.PhotoImage(file='icon.png')

    # 创建主窗口
    mainframe = tk.Frame(root, bg='#f9f9f9')
    mainframe.pack(fill='both', expand=True)
    mainframe.register_drop_target(tkinterDnD.FILE)
    mainframe.bind('<<Drop>>', dropHandler)

    # 显示提示语
    button = tk.Label(mainframe, text='\n' + '将 PDF 文件拖到这个窗口上' + '\n\n' + '解除 PDF 编辑限制',
                    image=logo, compound='top', anchor='center', font=(defaultfont, 13), bg='#f9f9f9')
    button.place(relx=.5, rely=.4, anchor='center')

    # 开始按钮
    ttk.Style().configure("StartBtn.TButton", font=(defaultfont, 11), padding=10)
    button = ttk.Button(mainframe, text='打开文件', style="StartBtn.TButton", command=btn_openfile)
    button.place(relx=.5, rely=.8, anchor='center')

    # 预先创建详情界面
    procframe = tk.Frame(root, bg='#f9f9f9')
    #procframe.pack(fill='both', expand=True)
    procframe.register_drop_target(tkinterDnD.FILE)
    procframe.bind('<<Drop>>', dropHandler)
    scrollbar = ttk.Scrollbar(procframe)
    scrollbar.pack(side='right', fill='y')
    tree = ttk.Treeview(procframe, selectmode="extended", columns=('path', 'passwd', 'state'), yscrollcommand=scrollbar.set)
    tree.pack(side='left', fill='both')
    scrollbar.config(command=tree.yview)
    tree['show'] = 'headings'
    tree.column("path", minwidth=0, width=190, stretch='no')
    tree.column("passwd", minwidth=0, width=190, stretch='no', anchor='center')
    tree.column("state", minwidth=0, width=100, stretch='no', anchor='center')
    tree.heading('path', text='文件')
    tree.heading('passwd', text='密码')
    tree.heading('state', text='状态')

    # 显示窗口
    root.deiconify()
    root.mainloop()

if __name__ == '__main__':
    ui()