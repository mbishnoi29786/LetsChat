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

    return Object.values(criteria).every(Boolean);
}


document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const password = document.querySelector('#password');
    const email = document.querySelector('#email');

    // Error elements
    const emailError = document.querySelector('#email-error');
    const passwordError = document.querySelector('#password-error');


    // Clear errors on input
    [ email, password].forEach(input => {
        input.addEventListener('input', () => {
            clearError(input);
        });
    });

    function clearError(input) {
        const errorDiv = document.querySelector(`#${input.id}-error`);
        errorDiv.textContent = '';
        input.style.border = '1px solid #ced4da';
    }


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

    // Form validation on submit
    form.addEventListener('submit', (e) => {
        let valid = true;

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
            passwordError.textContent = "Invalid Password!";
            password.style.border = '2px solid red';
            valid = false;
        }

        if (!valid) {
            e.preventDefault();
        }
    });
});


