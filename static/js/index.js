document.addEventListener('DOMContentLoaded', () => {
    const chatarea = document.querySelector(".chatarea");
    const friends = document.querySelectorAll(".friend");
    const searchInput = document.querySelector('#searchInput');
    const socket = io();

    // for the working of search button
    searchInput.addEventListener('input', function() {
        const searchTerm = searchInput.value.toLowerCase(); // for case sensitive search

        // Filter the friends list
        friends.forEach(friend => {
            const username = friend.querySelector(".friend-username").textContent.toLowerCase();
            if (username.includes(searchTerm)) {
                friend.style.display = ''; 
            } else {
                friend.style.display = 'none';
            }
        });
    });

    // Flag to track if it's the first message in the chat
    let isFirstMessage = true;

    // Listen for new message
    socket.on('receive_message', (data) => {
        appendMessage(data.message_id, data.sender, data.senderUsername, data.senderProfilePic, data.message, data.time, data.chat_day,  data.is_read, data.is_delivered, socket);
    });

    // to load the selected chat
    friends.forEach(friend => {
        friend.addEventListener('click', () => {
            const username = friend.dataset.username;
            
            fetch('/load_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username: username })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Set header and chat area
                const header = selectedChatHeader(data.username, data.status, data.profile_picture);
                const chatboxDiv = createElement("div", "chatbox");
                
                // If there are no messages, show the encryption message along with header and message-fields
                if (data.messages.length === 0) {
                    chatarea.innerHTML = ''; 
                    chatarea.appendChild(header);
                    chatarea.appendChild(encMsgDiv()); 
                    chatarea.appendChild(sendMessageFields());
                } else {
                    
                    // If messages exist, display them
                    data.messages.forEach(msg => {         
                            appendMessage(msg.id, msg.sender_id, msg.sender_username, msg.sender_profile_picture, msg.content, msg.time, msg.chat_day, msg.is_read, msg.is_delivered, socket);
                            if (!msg.is_read && msg.sender_id != msg.user_id) {
                                socket.emit('message_read', { "message_id": msg.id });
                            }
                    });

                    // Append header, messages, and message fields
                    chatarea.innerHTML = '';
                    chatarea.appendChild(header);
                    chatarea.appendChild(chatboxDiv);
                    chatarea.appendChild(sendMessageFields());
                }

                // Join the chat room for the selected user
                socket.emit('join_chat', {username: username});

                 // Handle sending message
                document.querySelector("#chat-form").addEventListener('submit', (e) =>  {
                    e.preventDefault();
                    
                    const message = document.querySelector("#message").value;
                    const receiver = document.querySelector(".selected-chat-username").innerHTML;
                    
                    if (message.trim() === "") return;
                    
                    socket.emit('send_message', {
                        message: message,
                        receiver: receiver
                    });
                    
                    document.querySelector("#message").value = '';
                    
                    // If it's the first message, replace the encryption message
                    if (isFirstMessage) {
                        // Clear the encryption message (encMsgDiv)
                        const encMsgDiv = document.querySelector('.enc-msg-div');
                        if (encMsgDiv) {
                            chatarea.replaceChild(chatboxDiv, encMsgDiv);
                        }
                        isFirstMessage = false; // Mark the first message as sent
                    }
                });
            })
            .catch(err => console.error("Error loading chat:", err));
            
            friends.forEach(f => f.classList.remove('selected'));
            friend.classList.add('selected');
        });
    });
    // Handle leaving the chat room when the user navigates away or closes the chat
    window.addEventListener('beforeunload', () => {
        const room = document.querySelector('.selected-chat-username').innerText;
        socket.emit('leave_chat', { room: room });
    });
});


// Append message dynamically
function appendMessage(messageId, sender, senderUsername, senderProfilePicture, message, time, chatDay, isRead, isDelivered, socket) {
    fetch('/api/get_user_info')
    .then(response => response.json())
    .then(data => {
        const sessionUserId = data.user_id;
        const sessionUsername = data.username;
        const sessionProfilePicture = data.profile_picture
        let chatbox = document.querySelector(".chatbox");
        if (!chatbox) {
            chatbox = createElement("div", "chatbox");
        }

        // const msgDiv = document.createElement("div");
        const className = sender === sessionUserId ? 'outgoing' : 'incoming';
        const username = sessionUsername === senderUsername ? sessionUsername : senderUsername;
        const profilePicture = sessionProfilePicture === senderProfilePicture ? sessionProfilePicture : senderProfilePicture;

        const msgDiv = messageBubble(className, username, profilePicture, message, chatDay, time, isRead, isDelivered);
        
        chatbox.appendChild(msgDiv);
        chatbox.scrollTop = chatbox.scrollHeight;

        // Emit message as delivered once it is displayed on the recipient's screen
        
        if (!isDelivered && sender !== sessionUserId) {
            socket.emit('message_delivered', { "message_id": messageId });
        }
    })
    .catch(error => console.error('Error fetching user info:', error));
}


function selectedChatHeader(username, status, profile_picture) {
    const header = createElement("header", "chatarea-header");
    const profileImage = createElement("img", "chat-profile-pic", "", {"alt" : "Profile Pic", "src" : `/static/images/profile_pictures/${profile_picture}`});
    const detailsDiv = createElement("div", "details");
    const chatUsernameSpan = createElement("span", "selected-chat-username", "", {"innerHTML": username});
    const statusPara = createElement("p", "chat-status", "", {"innerHTML": status});
    detailsDiv.appendChild(chatUsernameSpan);
    detailsDiv.appendChild(statusPara);

    header.appendChild(profileImage);
    header.appendChild(detailsDiv)

    return header
}

function messageArea() {
    const chatboxDiv = createElement("div", "chatbox");
    const encMsgDiv = createElement("div", "enc-msg-div", "", {"innerHTML": `<a href="#" class="float enc-msg"> 
                            <i class="fa fa-lock"></i>&nbsp;&nbsp;Messages are end-to-end Encrypted<br>
                            No one outside of this chat, not even ADMIN can read them.
                        </a>`})
    
    chatboxDiv.appendChild(encMsgDiv);

    return messageArea
}

// From Stack overflow
function messageBubble(classname,username, profilePicture, message, chatDay, time, isRead, isDelivered) {

    let statusIcon = '';
    if (isDelivered && !isRead) {
        statusIcon = '<div class="checkmark">L</div>';  // Delivered icon
    } else if (isRead) {
        statusIcon = '<div class="checkmark">L</div><div class="checkmark">L</div>';  // Read icon
    }

    const messageDiv = createElement("div", "message-container " + classname, "", 
        {"innerHTML" : `<div class="chat-log">
                            <div class="left-side">
                            <div class="text">
                                ${username}
                            </div>
                            <div class="thumbnail">
                                <span class="caption"><img src="../static/images/profile_pictures/${profilePicture}" alt="Profile Pic"></span>
                            </div>
                            </div>
                            <div class="right-side">
                                <div class="msg">
                                    ${message}
                                    <div class="msg-status">
                                        ${statusIcon}
                                    </div>
                                </div>
                                <div class="time">${chatDay} ${time}</div>
                            </div>
                        </div>`})

    return messageDiv
}


function encMsgDiv() {
    const encMsgDiv = createElement("div", "enc-msg-div");
    const encMsg = createElement("a", "enc-msg", "", {"innerHTML" : `<i class="fa fa-lock"></i>&nbsp;&nbsp;Messages are end-to-end Encrypted<br>
                            No one outside of this chat, not even ADMIN can read them.`})
    encMsgDiv.appendChild(encMsg);
    return encMsgDiv
}

function sendMessageFields () {
    const sendMessageDiv = createElement("div", "typing-area");

    const chatForm = createElement("form", "", "chat-form", {"action" : "#"})
    const messageInput = createElement("input", "form-control mr-sm-2", "message", {"type": "text", "placeholder": "Type a Message...", "name": "message"})
    const sendMessageBtn = createElement("button", "btn btn-outline-success my-2 my-sm-0", "", {"innerHTML" : "<i class='fab fa-telegram-plane'></i>", "type":"submit"})

    chatForm.appendChild(messageInput);
    chatForm.appendChild(sendMessageBtn);

    sendMessageDiv.appendChild(chatForm);

    return sendMessageDiv
}


function createElement(tag, className, id, options = {}) {
    const element = document.createElement(tag);
    element.className = className;
    element.id = id;
    Object.assign(element, options);
    return element;
}

function createTextInput(placeholder, className, id) {
    return createElement('input', className, id, { type: 'text', placeholder });
}


