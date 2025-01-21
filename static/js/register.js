document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const password = document.querySelector('#password');
    const confirmPassword = document.querySelector('#confirmation');
    const username = document.querySelector('#username');
    const email = document.querySelector('#email');

    // Error elements
    const usernameError = document.querySelector('#username-error');
    const emailError = document.querySelector('#email-error');
    const passwordError = document.querySelector('#password-error');
    const confirmError = document.querySelector('#confirmation-error');


    // Clear errors on input
    [username, email, password, confirmPassword].forEach(input => {
        input.addEventListener('input', () => {
            clearError(input);
        });
    });

    function clearError(input) {
        const errorDiv = document.querySelector(`#${input.id}-error`);
        errorDiv.textContent = '';
        input.style.border = '1px solid #ced4da';
    }

    // Password matching check
    confirmPassword.addEventListener('input', () => {
        if (password.value !== confirmPassword.value) {
            confirmPassword.style.border = '2px solid red';
            confirmError.textContent = "Passwords do not match!";
        } else {
            confirmPassword.style.border = '2px solid green';
            confirmError.textContent = "";
        }
    });

    // Email validation on input
    email.addEventListener('input', () => {
        if (!validateEmail(email.value)) {
            email.style.border = '2px solid red';
            emailError.textContent = "Invalid email format!";
        } else {
            email.style.border = '2px solid green';
            emailError.textContent = "";
        }
    });

    password.addEventListener('keyup', () => {
        validatePassword(password.value);
        document.querySelector(".password-requirements").style.display = "flex";
        if (validatePassword(password.value)) {
            document.querySelector(".password-requirements").style.display = "none";
        }
    });

    // Form validation on submit
    form.addEventListener('submit', (e) => {
        let valid = true;

        // Username validation
        if (!username.value.trim()) {
            usernameError.textContent = "Username is required!";
            username.style.border = '2px solid red';
            valid = false;
        }

        // Email validation on submit
        if (!email.value.trim() || !validateEmail(email.value)) {
            emailError.textContent = "Invalid email!";
            email.style.border = '2px solid red';
            valid = false;
        }

        // Password validation
        if (!password.value.trim()) {
            passwordError.textContent = "Password is required!";
            password.style.border = '2px solid red';
            valid = false;
        }

        if (!validatePassword(password.value.trim())) {
            passwordError.textContent = "Password doesn't meet the required criteria!";
            password.style.border = '2px solid red';
            valid = false;
        }

        if (password.value !== confirmPassword.value) {
            confirmError.textContent = "Passwords do not match!";
            confirmPassword.style.border = '2px solid red';
            valid = false;
        }

        if (!valid) {
            e.preventDefault();
        }
    });
});


// Email validation function
// Referance https://stackoverflow.com/questions/46155/how-can-i-validate-an-email-address-in-javascript
const validateEmail = (email) => {
return String(email)
    .toLowerCase()
    .match(
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
};


function validatePassword(password) {
    const criteria = {
        length: password.length >= 8,
        lowercase: /[a-z]/.test(password),
        uppercase: /[A-Z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*()_+=\-[\]{};':"\\|,.<>?/]/.test(password),
    };

    for (let key in criteria) {
        const element = document.getElementById(`${key}-check`);
        if (criteria[key]) {
            element.classList.add("valid");
            element.classList.remove("invalid");
        } else {
            element.classList.add("invalid");
            element.classList.remove("valid");
        }
    }

    return Object.values(criteria).every(Boolean);
}
