document.addEventListener("DOMContentLoaded", function() {
    // all profile options from the sidebar
    const profileOptions = document.querySelectorAll(".profile-option");

    // container where sections will be loaded
    const profileContent = document.getElementById("profile-content");

    // Event listener for each sidebar link
    profileOptions.forEach(option => {
        option.addEventListener("click", function(e) {
            e.preventDefault();

            const section = this.getAttribute("data-section");

            profileOptions.forEach(item => item.classList.remove("active"));
            this.classList.add("active");

            const formData = new FormData();
            formData.append("section", section);

            fetch("/profile", {
                method: "POST",
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                // Replace the content of the profile content section with the new section
                profileContent.innerHTML = html;
                
                // Call the functions to initialize validation for date and file inputs
                initializeDOBValidation();
                initializeFileValidation();
            })
            .catch(error => {
                console.error("Error loading the section:", error);
            });
        });
    });

    // Function to initialize Date of Birth validation
    function initializeDOBValidation() {
        const dobInput = document.querySelector('input[name="date_of_birth"]');
        if (dobInput) {
            // Calculate the max date to be 16 years ago from today
            const today = new Date();
            today.setFullYear(today.getFullYear() - 16);
            const maxDate = today.toISOString().split('T')[0];
            dobInput.setAttribute("max", maxDate); // Set max date to 16 years ago
        }
    }

    // Function to initialize file validation (size and type)
    function initializeFileValidation() {
        const fileInput = document.querySelector('input[type="file"][name="profile_picture"]');
        if (fileInput) {
            fileInput.addEventListener("change", function(e) {
                const file = e.target.files[0];

                if (file) {
                    // Check file type
                    const allowedExtensions = ['image/jpeg', 'image/png', 'image/gif'];
                    if (!allowedExtensions.includes(file.type)) {
                        alert("Invalid file type. Please upload a JPEG, PNG, or GIF image.");
                        fileInput.value = ''; // Reset the input
                        return;
                    }

                    // Check file size (max 5MB)
                    const maxFileSize = 5 * 1024 * 1024; // 5MB
                    if (file.size > maxFileSize) {
                        alert("File is too large. Maximum size is 5MB.");
                        fileInput.value = ''; 
                        return;
                    }
                }
            });
        }
    }
});