import os
import magic
import pikepdf
from xstr import xstr

passwdStorage = ['']

def isPDF(path):
    return os.path.exists(path) and magic.from_buffer(open(path, "rb").read(2048), mime=True) == 'application/pdf'

def unlockPDF(path, dictionary=passwdStorage):
    for passwd in dictionary:
        try:
            try:
                pdf = pikepdf.open(path, password=passwd)
                return xstr* 'Unlocked' << (passwd, pdf)
            except pikepdf.PasswordError:
                continue
        except Exception as e:
            return xstr* 'Error' << e
    return 'NoPassword'

def savePDF(path, pdf):
    dir, fullname = os.path.split(path)
    name, ext = os.path.splitext(fullname)
    newpath = os.path.join(dir, f'{name}_已解密{ext}')
    pdf.save(newpath)
    return newpath
