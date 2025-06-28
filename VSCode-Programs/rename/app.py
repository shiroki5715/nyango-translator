from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('files')
        new_name = request.form.get('new_name')
        prepend_number = request.form.get('prepend_number') == 'prepend'
        renamed_files = rename_files([file.filename for file in files], new_name, prepend_number)
        return render_template_string('<p>{{ renamed_files }}</p>', renamed_files=renamed_files)
    return '''
    <!doctype html>
    <title>Upload Files</title>
    <h1>Upload Files</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=files multiple>
      <input type=text name=new_name placeholder="New name">
      <select name=prepend_number>
        <option value=prepend>Prepend number</option>
        <option value=append>Append number</option>
      </select>
      <input type=submit value=Upload>
    </form>
    '''

def rename_files(file_list, new_name, prepend_number):
    new_file_list = []
    for i, file in enumerate(file_list, start=1):
        if prepend_number:
            new_file_name = f"{i}_{new_name}"
        else:
            new_file_name = f"{new_name}_{i}"
        new_file_list.append(new_file_name)
    return new_file_list

if __name__ == '__main__':
    app.run(debug=True)
