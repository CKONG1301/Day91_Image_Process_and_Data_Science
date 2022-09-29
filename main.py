from flask import Flask, render_template, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import SubmitField
import os
from dotenv import load_dotenv
from PIL import Image
import PIL
import numpy as np
import pandas as pd


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap(app)


class UploadForm(FlaskForm):
    file = FileField('File to upload:', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'bmp'], 'Images only!')], render_kw={'class': 'form-control-file'})
    submit = SubmitField('Submit')


def process_img(filename):
    try:
        with Image.open(filename) as user_img:
            # Save a local copy for display purpose.
            extension = PIL.ImageFile.ImageFile.get_format_mimetype(user_img).split('/')[1]
            img_file = f'static/images/temp.{extension}'
            user_img.save(img_file)
            # Get image data into numpy array.
            img_array = np.array(user_img)
            # Create a list of pixes
            color_list = []
            n = 0
            for x in range(img_array.shape[0]):
                for y in range(img_array.shape[1]):
                    img_color = 0
                    for i in range(3):
                        img_color = img_color * 256 + img_array[x, y, i]
                    # Convert to 6 character hex code with leading zeros.
                    color = hex(img_color).replace('0x', '').zfill(6)
                    # Format color code to html format.
                    color = '#' + color.upper()
                    color_list.append(color)
                    n += 1
            # Create a series of palette with color vs counts
            palette = pd.DataFrame(color_list, columns=['color_code']).value_counts()
            # Create palette DataFrame. Need reset_index to get a default index df.
            palette = pd.DataFrame(palette.reset_index().values, columns=['color_code', 'counts'])
            # Insert percent column. astype to change type to float than round to 4 decimal.
            palette.insert(len(palette.columns), 'percent', round((palette.counts / palette.counts.sum()).astype(float), 4))
            return palette, img_file
    except PIL.UnidentifiedImageError:
        return 'error', filename
        
        
@app.route('/', methods=['GET', 'POST'])
def home():
    form = UploadForm()
    filename = 'static/images/projects.jpg'
    if form.validate_on_submit():
        filename = form.file.data
    palette, filename = process_img(filename)
    return render_template('index.html', form=form, img=filename, palette=palette)


if __name__ == "__main__":
    app.run(debug=True)



