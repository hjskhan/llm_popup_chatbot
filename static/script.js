class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            minimizeButton: document.getElementById('minimizeButton'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button'),
            messageContainer: document.querySelector('.chatbox__messages') // Added message container reference
        }

        this.state = false;
        this.messages = [];
    }

    display() {
        const {openButton, chatBox, sendButton, minimizeButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        minimizeButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('textarea');
        node.addEventListener("keyup", ({key}) => {
            if (event.key === "Enter" && !event.shiftKey) {
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
        var textField = chatbox.querySelector('textarea');
        let message = textField.value;
        if (message === "") {
            return;
        }
        let formData = new FormData();
        formData.append('message', message);
        let msg1 = { name: "User", message: message }
        this.messages.push(msg1);
        this.updateChatText(chatbox);
        textField.value = '';
        showLoader();
        
        fetch('/chat', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(r => {
            hideLoader();
            let msg2 = { name: "Sam", message: r.response };
            this.messages.push(msg2);
            this.updateChatText(chatbox);
            textField.value = '';
        })
        .catch((error) => {

            hideLoader();
            console.error('Error:', error);
            this.updateChatText(chatbox);
            textField.value = '';
        });
    }
    


    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, index) {
            let messageContent = item.message.replace(/\n/g, '<br>');
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
        document.getElementById('file_upload_button').disabled = true;
        document.getElementById('popup-btn').disabled = true;
        document.querySelector('.chatbox__send--footer').disabled = true;
        var form = new FormData();
        form.append('file', file);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.onload = function() {
            hideLoader();
            document.getElementById('file_upload_button').disabled = false;
            document.getElementById('popup-btn').disabled = false;
            document.querySelector('chatbox__send--footer').disabled = false;
            if (xhr.status === 200) {
                alert(xhr.responseText);
                window.location.reload();
            } else {
                alert('Error uploading file!');
            }
        };

        xhr.send(form);
        
    }
}


document.addEventListener("DOMContentLoaded", function () {
    
    const popupBtn = document.getElementById('popup-btn');
    const popup = document.getElementById('popup');
    const closeBtn = document.getElementById('upload_url');
    
    popupBtn.addEventListener('click', openPopup);
    closeBtn.addEventListener('click', closePopup);

});


function openPopup() {
    popup.style.display = 'flex';
  }

function closePopup() {
    popup.style.display = 'none';
  }

function uploadURL() {
    closePopup();
    var urlInput = document.getElementById('urlInput');
    var url = urlInput.value.trim();
    
    if (url) {
        document.getElementById('file_upload_button').disabled = true;
        document.getElementById('popup-btn').disabled = true;
        document.querySelector('chatbox__send--footer').disabled = true;
        showLoader();
        var form = new FormData();
        form.append('url', url);

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload_url', true);

        xhr.onload = function() {
            hideLoader();
            document.getElementById('file_upload_button').disabled = false;
            document.getElementById('popup-btn').disabled = false;
            document.querySelector('chatbox__send--footer').disabled = false;
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
    urlInput.value = '';
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

// function to toggle size of chatbox
function toggleChatboxSize() {
    var chatboxSupport = document.querySelector('.chatbox__support');
    chatboxSupport.classList.toggle('expanded');
}

const chatbox = new Chatbox();
chatbox.display();  