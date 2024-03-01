function uploadFile() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];

    if (file) {
        var form = new FormData();
        form.append('file', file);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.onload = function() {
            if (xhr.status === 200) {
                alert(xhr.responseText);
            } else {
                alert('Error uploading file!');
            }
        };

        xhr.send(form);
    } else {
        alert('Please select a file!');
    }
}