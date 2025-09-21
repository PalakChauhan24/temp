// script.js

document.addEventListener('DOMContentLoaded', () => {
    // If we're on home.html, show username and fetch buses
    if (location.pathname.endsWith('home.html')) {
        const username = localStorage.getItem('username');
        if (!username) return window.location.href = 'login.html';

        document.getElementById('username').textContent = username;

        // Example: fetch bus data functionality (replace with your API if applicable)
        // fetch('/api/buses')
        //     .then(res => res.json())
        //     .then(data => {
        //         // Populate bus info here
        //     });
    }
});
