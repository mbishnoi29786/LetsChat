document.addEventListener("DOMContentLoaded", function() {

    // Handling form submission for adding a friend
    const addFriendForm = document.getElementById("add-friend-form");
    const messageDiv = document.getElementById("message-div"); // Div for displaying messages
    if (addFriendForm) {
        addFriendForm.addEventListener("submit", function(e) {
            e.preventDefault(); // Prevent normal form submission

            // Trim input values
            const formData = new FormData(addFriendForm);
            const friendUsername = formData.get("friend_username").trim(); // Trim the username before sending it

            // Check if the username is empty after trimming
            if (friendUsername === "") {
                displayMessage("error", "Username cannot be empty!");
                return;
            }

            // Send AJAX request
            fetch("/add_friend", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ friend_username: friendUsername })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Display success message
                    displayMessage("success", data.message);
                    // Optionally, update the UI (e.g., clear the form or update friends list)
                    addFriendForm.reset(); // Reset the form after success
                } else {
                    // Display error message
                    displayMessage("error", data.message);
                }
            })
            .catch(error => {
                console.error("Error during friend request:", error);
                displayMessage("error", "An error occurred while sending the friend request.");
            });
        });
    }

    // Handling button click for adding a friend directly
    const potentialFriendBtns = document.querySelectorAll(".potential-friend-btn");
    potentialFriendBtns.forEach(button => {
        button.addEventListener("click", function() {
            const friendUsername = this.getAttribute("data-username");

            // Send AJAX request to add this potential friend
            fetch("/add_friend", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ friend_username: friendUsername })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const friendElement = button.closest(".friend");
                    friendElement.remove();
                    displayMessage("success", data.message);
                } else {
                    displayMessage("error", data.message);
                }
            })
            .catch(error => {
                console.error("Error during friend request:", error);
                displayMessage("error", "An error occurred while sending the friend request.");
            });
        });
    });

    function displayMessage(type, message) {
        messageDiv.innerHTML = message;
        
        // Remove any previous classes
        messageDiv.classList.remove('success', 'error', 'show');
        
        // classes based on the message type
        messageDiv.classList.add(type);  // either "success" or "error"
        messageDiv.classList.add('show');  
        
        // to hide it after a few seconds
        setTimeout(() => {
            messageDiv.classList.remove('show');  
        }, 3000);
    }
});
