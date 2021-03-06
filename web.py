from flask import Flask,render_template,request
import shutil
import os
import amiibos

app = Flask(__name__)
script = ""

def default():
    msg = read('msg.txt')
    script = read('scriptcopy.txt')
    return msg,script

def read(file):
    with open('file/'+file,'r') as f:
        return f.read()
def write(file,msg):
    with open('file/'+file,'w') as f:
        f.write(msg)
def clean(file):
    with open('file/'+file,'w+') as f:
        f.truncate()

@app.route('/')
def index():
    msg,script=default()
    return render_template('index.html',msg = msg,script =script)

@app.route('/bluez',methods=['POST'])
def bluez():
    if request.method == 'POST':
        #暂时无法使用
        #write('message.txt'request.form['btn']+'\n')
        write('message.txt','该功能暂时无法使用\n')
        write('command.txt',request.form['btn'])

    msg,script=default()
    return render_template('index.html',msg = msg,script =script)

@app.route('/btn',methods=['POST'])
def btn():
    if request.method == 'POST':
        btn = request.form['btn']
        write('command.txt',btn)
        if btn == 'amiibo clean':
            path = 'file/amiibo/'
            shutil.rmtree(path)
            os.mkdir(path)
            msg,script=default()
            return render_template('index.html',msg =msg,script =script,amiibo='cleaned!')
        elif btn == 'amiibo remove':
            write('command.txt','amiibo remove')
            msg,script=default()
            return render_template('index.html',msg = msg,script =script,amiibo='removed!')

    msg,script=default()
    return render_template('index.html',msg = msg,script =script)

@app.route('/script/run',methods=['POST'])
def run():
    if request.method == 'POST':
        script = request.form['script']
        write('script.txt',script)
        write('scriptcopy.txt',script)
        write('command.txt','run')

    msg,script=default()
    return render_template('index.html',msg = msg,script =script)

@app.route('/script/stop',methods=['POST'])
def stop():
    if request.method == 'POST':
        write('command.txt','stop')

    msg,script=default()
    return render_template('index.html',msg = msg,script =script)

#Amiibo
@app.route('/amiibo/upload',methods=['POST'])
def upload():
    file = request.files['file']
    filename = file.filename
    if filename.rsplit('.', 1)[1].lower() in {'bin','BIN'}:
        filename = filename.replace(' ','_').lower()
        file.save('file/amiibo/'+filename)
        write('command.txt','amiibo '+filename)
        msg,script=default()
        return render_template('index.html',msg = msg,script =script,amiibo='OK!')
    else:
        msg,script=default()
        return render_template('index.html',msg = msg,script =script,amiibo='NO! This isn`t bin file.') 
#动森批量刷amiibo跳转
@app.route('/amiibos')
def toAmiibosUpload():
    return render_template('amiibos.html')

#上传amiibo压缩包
@app.route('/amiibos',methods=['POST'])
def amiibosUpload():
    file = request.files['file']
    filename = file.filename
    if filename.rsplit('.',1)[1].lower() == 'zip':

        #清除残余amiibo数据
        path = 'file/amiibo/'
        shutil.rmtree(path)
        os.mkdir(path)

        #保存zip压缩包
        filename = filename.replace(' ','_').lower()
        file.save(path+filename)

        #解压并生成脚本
        amiibos.run(filename)
        return render_template('amiibos.html',msg = '上传成功，脚本生成完毕，请按下方按钮跳转查看')
    else:
        return render_template('amiibos.html',msg = '上传失败，仅支持zip压缩文件')

#raspi
@app.route('/raspi',methods=['POST'])
def raspi():
    if request.method == 'POST':
        cmd = request.form['btn']
        os.system(cmd)

if __name__ == '__main__':
    clean('message.txt')
    clean('command.txt')
    clean('script.txt')
    app.run(debug=True,host='0.0.0.0')
