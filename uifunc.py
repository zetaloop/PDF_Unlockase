import os
import tkinter as tk
from tkinter import ttk, filedialog, font, messagebox
import tkinterDnD

def mktitle(x):
    return 'PDF 解锁酶' + ' - ' + x

def checkfilelist(lst):
    targets = []
    for num,i in enumerate(sorted(set(lst))):
        i = os.path.normpath(i)
        state.set(f'[{len(targets)}/{num+1}] {i}')
        root.update()
        if os.path.exists(i) and magic.from_buffer(open(i, "rb").read(2048), mime=True) == 'application/pdf':
            targets.append(i)
    state.set(f'[{len(targets)}/{len(lst)}] ' + f'已输入 {len(targets)} 个有效的 PDF 文件')
    if targets:
        root.after(0, lambda:start(targets))
    else:
        messagebox.showwarning(mktitle('文件无效'), '没有检测到任何有效 PDF 文档！')

def frm_drop(event):
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
    checkfilelist(targets)

def btn_openfile(_=...):
    # Open a file dialog and update the file path
    files = filedialog.askopenfilenames(title='选择要解锁的 PDF 文件', filetypes=(('PDF 文档', '*.pdf'), ('所有文件', '*.*')))
    if files:
        checkfilelist(files)




def start(targets):
    import pikepdf
    mainframe.pack_forget()
    procframe.pack(fill='both', expand=True)
    root.title(mktitle('文件解锁中'))
    for num, i in enumerate(targets):
        name = os.path.basename(i)
        tree.insert('', 'end', num, values=(name, '', ''))
    for num, i in enumerate(targets):
        name = os.path.basename(i)
        tree.see(num)
        tree.set(num, 'stat', '...')
        if trypassword(i):
            tree.set(num, 'pass', '无密码')
            password = ''
        elif password:=trypasswords(i, passwords):
            tree.set(num, 'pass', password)
        elif password:=askpassword(i):
            tree.set(num, 'pass', password)
        else:
            tree.set(num, 'pass', '错误')
            tree.set(num, 'stat', '密码错误无法打开')
            password = None
        if password is not None:
            pdf = pikepdf.open(file_path)
        
    

def trypassword(path, password=''):
    try:
        pikepdf.open(i, password=password).close()
        return True
    except pikepdf.PasswordError:
        return False

def trypasswords(path, passwordlist):
    for password in passwordlist:
        if password and trypassword(path, password):
            return password
        else:
            return False


passwords = []

root = tkinterDnD.Tk()  # Drag and drop plugin init
root.withdraw()
root.geometry('500x500')
root.resizable(False, False)
root.title(mktitle('文件拖入此窗口'))
root.iconbitmap('icon.ico')
root.bind("<Control-w>", lambda _: exit())
root.bind("<Escape>", lambda _: exit())
root.bind("<Return>", btn_openfile)

defaultfont = font.nametofont("TkDefaultFont").actual()["family"]
logo = tk.PhotoImage(file='icon.png') 
state = tk.StringVar()
state.set('[0/0] ' + '请打开 PDF 文件')

# Create a frame that fills the whole window
mainframe = tk.Frame(root, bg='#f9f9f9')
mainframe.pack(fill='both', expand=True)
mainframe.register_drop_target(tkinterDnD.FILE)
mainframe.bind('<<Drop>>', frm_drop)

# Label to show the prompt text
button = tk.Label(mainframe, text='\n' + '将 PDF 文件拖到这个窗口上' + '\n\n' + '解除 PDF 编辑限制',
                  image=logo, compound='top', anchor='center', font=(defaultfont, 13), bg='#f9f9f9')
button.place(relx=.5, rely=.4, anchor='center')

# Button to start the PDF unlock process
ttk.Style().configure("StartBtn.TButton", font=(defaultfont, 11), padding=10)
button = ttk.Button(mainframe, text='打开文件', style="StartBtn.TButton", command=btn_openfile)
button.place(relx=.5, rely=.8, anchor='center')

# State bar
label = tk.Label(root, textvariable=state, anchor='w', font=(defaultfont, 8), bg='#f0f0f0')
label.pack(side='bottom', fill='x')

#
procframe = tk.Frame(root, bg='#f9f9f9')
#procframe.pack(fill='both', expand=True)

#
scrollbar = ttk.Scrollbar(procframe)
scrollbar.pack(side='right', fill='y')
tree = ttk.Treeview(procframe, selectmode="extended", columns=('file', 'pass', 'stat'), yscrollcommand=scrollbar.set)
tree.pack(side='left', fill='both')
scrollbar.config(command=tree.yview)
tree['show'] = 'headings'
tree.column("file", minwidth=0, width=190, stretch='no')
tree.column("pass", minwidth=0, width=190, stretch='no', anchor='center')
tree.column("stat", minwidth=0, width=100, stretch='no', anchor='center')
tree.heading('file', text='文件')
tree.heading('pass', text='密码')
tree.heading('stat', text='状态')

root.deiconify()
root.mainloop()