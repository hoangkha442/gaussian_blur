from flask import Flask, render_template, request, render_template_string
from flask_wtf import FlaskForm
from wtforms import SelectField, FileField, SubmitField
from wtforms.validators import InputRequired
from PIL import Image
import numpy as np
import cv2
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create a form for selecting transformations
class TransformationForm(FlaskForm):
    options = [("Week Blur", "Week Blur"), ("Median Blur", "Median Blur"),
               ("Strong Blur", "Strong Blur")]
    
    image = FileField(validators=[InputRequired()])
    transformation = SelectField("Select Transformation:", choices=options, validators=[InputRequired()])
    submit = SubmitField("Apply Transformation")
# HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Gaussian Blur</title>
    <link href="../dist/output.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body{
        color: white;
        }
        .container-60 {
            max-width: 60%;
            margin: 0 auto;
        }
        .w-50{
            width: 50%;
        }
        input.form-control{
            width: 100%
            cursor: pointer;
        }
        select.form-control{
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
        }
        input::file-selector-button {
            padding: 0.5em;
            border-radius: 4px;
            background-color: white;
            border: none;
            cursor: pointer;
        }
        .bg-black24{
            background-color: #000324
        }
        .bg-43{
            background-color: #242743
        }
        .w-50{
            width: 50%
        }
        .h-50{
            height: 50%
        }
        .mt-50{
        margin-top: 20%
        }
        .bg-gradient{
            background-image: linear-gradient(to right, 
#121745 , #262945);
        }
        .transform{
            background-color: #4f5de4
        }
        .transform:hover{
            background-color: #6f5de4
        }

    </style>
</head>
<body class='bg-black24 h-screen relative'>
    <div class='overlay absolute w-full h-full z-20'>
        <img class='w-50 h-full ml-auto' src='https://bracketweb.com/eduactwp/wp-content/uploads/2023/09/banner-bg-1.png'/>
    </div>
    <div class='overlay absolute w-full h-full z-10'>
        <img class='w-full h-50 text-end mt-50' src='https://bracketweb.com/eduactwp/wp-content/uploads/2023/09/counter-bg-1-dark.jpg'/>
    </div>
    <div class='container-60 relative z-50'>
        <div class='text-center text-white mb-4'>
        <h1 class='text-4xl pt-16 uppercase font-bold'>gaussian blur</h1>
    </div>
    <div class='bg-gradient flex p-1 gap-1 rounded-xl'>
        <div class='w-full shadow-2xl p-2'>
            <div class='w-full h-80 object-cover' id="original_image">
                <p class='font-bold mb-1 text-white'>Original Image</p>
            <div class='my-2'>
                {% if original_image %}
                <img class='w-full h-80 object-cover rounded-sm' src="data:image/png;base64,{{ original_image }}" alt="Original Image">
            {% endif %}
            </div>
            </div>
            <form method="POST" class='mt-10' enctype="multipart/form-data" onsubmit="return applyTransformation()">
            {{ form.hidden_tag() }}
            <div class='flex items-center justify-between gap-5'>
                <div class='w-50'>
                    {{ form.image(class="form-control") }}
                </div>
                <div class='w-50'>
                    <button type="submit" class="transform  transition-all duration-300 text-white py-2 px-4 rounded ">Apply Transformation </span></button>
                </div>
            </div>
            <div class='my-2 flex items-center justify-between'>
                {{ form.transformation.label }}
                <div class='mr-6 text-black'>
                    {{ form.transformation(class="form-control") }}
                </div>
            </div>
            </form>
           <!-- Thêm button Advanced Options -->
<div class='my-2 flex items-center justify-between'>
    <button type="button" class="transform transition-all duration-300 text-white py-2 px-4 rounded" onclick="toggleAdvancedOptions()">Advanced Options</button>
</div>

<!-- Thêm phần hiển thị Advanced Options -->
<div id="advancedOptions" style="display: none;">
    <div class='my-2 flex items-center justify-between'>
        <label for="kernel_size_x" class='mr-2 text-white'>Kernel Size X:</label>
        <input type="number" name="kernel_size_x" id="kernel_size_x" class='form-control text-black'>
    </div>
    <div class='my-2 flex items-center justify-between'>
        <label for="kernel_size_y" class='mr-2 text-white'>Kernel Size Y:</label>
        <input type="number" name="kernel_size_y" id="kernel_size_y" class='form-control text-black'>
    </div>
    <div class='my-2 flex items-center justify-between'>
        <label for="sigma" class='mr-2 text-white'>Sigma:</label>
        <input type="number" step="0.1" name="sigma" id="sigma" class='form-control text-black'>
    </div>
</div>

        </div>
        <div class='w-full shadow-2xl p-2' id="transformed_image">
            {% if transformed_image %}
                <p class='font-bold mb-1'>{{ title }}</p>
               <div class='my-2'> 
                <img class='w-full h-80 object-cover rounded-sm' src="data:image/png;base64,{{ transformed_image }}" alt="Transformed Image">
                </div>
                <div class='px-2'>
                    <button type="button" class="w-full py-2 bg-white mt-4 rounded font-bold text-black" id="saveButton" onclick="saveImage()">Lưu Ảnh</button>
                </div>
            {% endif %}
        </div>

    </div>
    </div>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
       function applyTransformation() {
        var formData = new FormData($('form')[0]);

        // Check if Advanced Options are displayed
        var advancedOptions = document.getElementById("advancedOptions");
        if (advancedOptions.style.display !== "none") {
            // Lấy giá trị từ các ô input của Advanced Options
            var kernelSizeX = $('#kernel_size_x').val();
            var kernelSizeY = $('#kernel_size_y').val();
            var sigma = $('#sigma').val();
            if (kernelSizeX && kernelSizeY && sigma % 2 == 0) {
                alert("Vui lòng nhập số lẻ");
                return false;
            }
            // Thêm giá trị vào FormData để gửi lên server
            formData.append('kernel_size_x', kernelSizeX);
            formData.append('kernel_size_y', kernelSizeY);
            formData.append('sigma', sigma);

            // Ghi đè lên thuộc tính kernel_size và sigma
            $('#kernel_size_x').val(kernelSizeX);
            $('#kernel_size_y').val(kernelSizeY);
            $('#sigma').val(sigma);
        } else {
            // If Advanced Options are not displayed, set default values based on the selected transformation
            var selectedTransformation = $('#transformation').val();
            // Set default values for kernel_size and sigma based on the selected transformation
            if (selectedTransformation === 'Median Blur') {
                $('#kernel_size_x').val(11);
                $('#kernel_size_y').val(11);
                $('#sigma').val(5);
            } else if (selectedTransformation === 'Strong Blur') {
                $('#kernel_size_x').val(25);
                $('#kernel_size_y').val(25);
                $('#sigma').val(13);
            } else if (selectedTransformation === 'Week Blur') {
                $('#kernel_size_x').val(1);
                $('#kernel_size_y').val(1);
                $('#sigma').val(1);
            }
        }
        $.ajax({
            type: 'POST',
            url: '/',
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                var result = $(data);
                $('#original_image').html(result.find('#original_image').html());
                $('#transformed_image').html(result.find('#transformed_image').html());
            }
        });
        return false;
        }

        function toggleAdvancedOptions() {
            var advancedOptions = document.getElementById("advancedOptions");
            if (advancedOptions.style.display === "none") {
                advancedOptions.style.display = "block";
                // Check if the selected transformation is "Week Blur"
                var selectedTransformation = $('#transformation').val();
                if (selectedTransformation === "Week Blur") {
                    // Set default values for Week Blur
                    $('#kernel_size_x').val(2);
                    $('#kernel_size_y').val(2);
                    $('#sigma').val(1);
                }
            } else {
                advancedOptions.style.display = "none";
            }
        }
        function saveImage() {
            var transformedImageSrc = $('#transformed_image img').attr('src');
            var link = document.createElement('a');
            link.href = transformedImageSrc;
            link.download = 'transformed_image.png';
            link.click();
        }
</script>
</body>
</html>
"""
# Route to handle the main page
@app.route('/', methods=['GET', 'POST'])
def main():
    form = TransformationForm()
    original_image_base64 = None
    transformed_image_base64 = None
    title = ""  # Initialize the title variable

    if request.method == 'POST' and form.validate_on_submit():
        image = form.image.data
        transformation = form.transformation.data

        if image:
            image_bytes = image.read()
            img = Image.open(BytesIO(image_bytes))
            im = np.asarray(img)

            # Extract kernel_size_x, kernel_size_y, and sigma from the form data
            kernel_size_x = request.form.get('kernel_size_x')
            kernel_size_y = request.form.get('kernel_size_y')
            sigma = request.form.get('sigma')

            # Apply the selected transformation
            if transformation == 'Median Blur':
                kernel_size_x = int(kernel_size_x) if kernel_size_x else 11
                kernel_size_y = int(kernel_size_y) if kernel_size_y else 11
                sigma = float(sigma) if sigma else 5
                title = 'Median Blur'
                im_transformed = cv2.medianBlur(im, kernel_size_x)
            elif transformation == 'Strong Blur':
                kernel_size_x = int(kernel_size_x) if kernel_size_x else 25
                kernel_size_y = int(kernel_size_y) if kernel_size_y else 25
                sigma = float(sigma) if sigma else 13
                title = 'Strong Blur'
                im_transformed = cv2.GaussianBlur(im, (kernel_size_x, kernel_size_y), sigma)
            elif transformation == 'Week Blur':
                kernel_size_x = int(kernel_size_x) if kernel_size_x else 1
                kernel_size_y = int(kernel_size_y) if kernel_size_y else 1
                sigma = float(sigma) if sigma else 1
                title = 'Weak Blur'
                im_transformed = cv2.GaussianBlur(im, (kernel_size_x, kernel_size_y), sigma)

            # Convert the images to base64 format
            original_image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Convert the transformed image to PIL Image
            transformed_img = Image.fromarray(im_transformed)

            # Convert the transformed image to base64 format
            transformed_image_io = BytesIO()
            transformed_img.save(transformed_image_io, format='PNG')
            transformed_image_base64 = base64.b64encode(transformed_image_io.getvalue()).decode('utf-8')

        return render_template_string(html_content, form=form, original_image=original_image_base64, transformed_image=transformed_image_base64, title=title)

    return render_template_string(html_content, form=form, original_image=original_image_base64, transformed_image=transformed_image_base64, title="")

if __name__ == '__main__':
    app.run(debug=True)