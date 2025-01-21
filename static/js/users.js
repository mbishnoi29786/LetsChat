document.addEventListener('DOMContentLoaded', ()=> {
    const friends = document.querySelectorAll(".friend");

    friends.forEach(friend => {
        friend.addEventListener('click', ()=> {
            const username = friend.dataset.username;

            fetch('/load_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({username:username})
            })
            .then(response => response.json())
            .then(data => {
                const chatbox = document.querySelector('.selected-chat .chatbox');
                const header = document.querySelector('.selected-chat header .details span b');
                const profileImg = document.querySelector('.selected-chat header img');

                // update UI with friend details
                header.textContent = data.username;
                profileImg.src = `/static/images/profile_pictures/${data.profile_picture}`;

                chatbox.innerHTML = ''; // Clear existing messages

                data.messages.forEach(msg => {
                    const messageElement = `<div class="message">
                        <b>${msg.sender}:</b> ${msg.content}
                    </div>`;
                    chatbox.innerHTML += messageElement;
                })
            })
        })
    })
})