// Function to toggle the theme and update localStorage
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    // Update the theme in localStorage
    localStorage.setItem('theme', newTheme);

    // Update the body's class
    document.body.classList.remove(currentTheme);
    document.body.classList.add(newTheme);

    // Update the toggle icon
    updateToggleIcon(newTheme);
}

// Function to update the toggle button icon
function updateToggleIcon(theme) {
    const icon = document.querySelector('#theme-toggle-btn i');
    if (icon) {
        if (theme === 'dark') {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        } else {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }
}

// Apply the stored theme when the page loads
function applyStoredTheme() {
    const storedTheme = localStorage.getItem('theme') || 'light'; // Default to light theme
    document.body.classList.add(storedTheme);
    updateToggleIcon(storedTheme); // Update the toggle button icon
}

// Initialize theme on page load
window.onload = function() {
    applyStoredTheme();
    
    // Add event listener for theme toggle button
    const toggleButton = document.getElementById('theme-toggle-btn');
    if (toggleButton) {
        toggleButton.addEventListener('click', toggleTheme);
    }
};
