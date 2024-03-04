class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            messageContainer: document.querySelector('.chatbox__messages') // Added message container reference
        }

        this.state = false;
        this.messages = [];
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }

    
    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input[type="text"]');
        // var fileInput = chatbox.querySelector('input[type="file"]');
        let message = textField.value;
    
        // if (message === "" && !fileInput.files.length) {
        //     return;
        // }
        if (message === "") {
            return;
        }
        let formData = new FormData();
        formData.append('message', message);
        // if (fileInput.files.length) {
        //     formData.append('file', fileInput.files[0]);
        // }
    
        let msg1 = { name: "User", message: message }
        this.messages.push(msg1);
        this.updateChatText(chatbox);
    
        fetch('/chat', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(r => {
            let msg2 = { name: "Sam", message: r.response };
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.value = '';
            // fileInput.value = ''; // Clear file input
        })
        .catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox);
            textField.value = '';
            // fileInput.value = ''; // Clear file input
        });
    }
    


    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            if (item.name === "Sam")
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
          });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}


function openFileInput() {
    var fileInput = document.getElementById('fileInput');
    fileInput.click();
}

function fileSelected(input) {
    var file = input.files[0];
    if (file) {
        uploadFile(file);
    }
}   
function uploadFile() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];

    if (file) {
        showLoader();
        var form = new FormData();
        form.append('file', file);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.onload = function() {
            hideLoader();
            if (xhr.status === 200) {
                alert(xhr.responseText);
                window.location.reload();
            } else {
                alert('Error uploading file!');
            }
        };

        xhr.send(form);
    // } else {
    //     alert('Please select a file!');
    }
}

function uploadURL() {
    var urlInput = document.getElementById('urlInput');
    var url = urlInput.value;

    if (url) {
        showLoader();
        var form = new FormData();
        form.append('url', url);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload_url', true);

        xhr.onload = function() {
            hideLoader();
            if (xhr.status === 200) {
                alert(xhr.responseText);
                window.location.reload();
            } else {
                alert('Error uploading URL!');
            }
        };

        xhr.send(form);
    } else {
        alert('Please enter a URL!');
    }
}

function showLoader() {
    // Create a container for the loader
    var loaderContainer = document.createElement('div');
    loaderContainer.className = 'loader-container';

    // Create and append the loader element
    var loaderDiv = document.createElement('div');
    loaderDiv.className = 'loader';
    loaderContainer.appendChild(loaderDiv);

    // Append the loader container to the chatbox
    var chatboxMessages = document.querySelector('.chatbox__header');
    chatboxMessages.appendChild(loaderContainer);
}

function hideLoader() {
    // Remove the loader container
    var loaderContainer = document.querySelector('.loader-container');
    if (loaderContainer) {
        loaderContainer.remove();
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const accordionInput = document.getElementById("uploadAccordion");

    accordionInput.addEventListener("change", function () {
        const accordionContent = document.querySelector(".accordion-content");
        accordionContent.style.maxHeight = accordionInput.checked ? accordionContent.scrollHeight + "px" : 0;
    });
});

const chatbox = new Chatbox();
chatbox.display();  