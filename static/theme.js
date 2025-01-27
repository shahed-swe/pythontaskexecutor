document.getElementById('theme-toggle').addEventListener('click', function() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    const navbar = document.querySelector('.navbar');
    const tables = document.querySelectorAll('.table');
    body.classList.toggle('dark');
    body.classList.toggle('light');
    navbar.classList.toggle('dark');
    navbar.classList.toggle('light');
    
    // Change icon based on theme
    if (body.classList.contains('dark')) {
        themeIcon.textContent = '🌙'; // Moon icon for dark theme
        localStorage.setItem('theme', 'dark');
    } else {
        themeIcon.textContent = '☀️'; // Sun icon for light theme
        localStorage.setItem('theme', 'light');
    }

    // Apply theme classes to tables
    tables.forEach(table => {
        table.classList.toggle('dark');
        table.classList.toggle('light');
    });
});

// Load the saved theme on page load
window.onload = function() {
    const savedTheme = localStorage.getItem('theme');
    const navbar = document.querySelector('.navbar');
    const tables = document.querySelectorAll('.table');
    const themeIcon = document.getElementById('theme-icon');
    if (savedTheme) {
        document.body.classList.add(savedTheme);
        navbar.classList.add(savedTheme);
        tables.forEach(table => {
            table.classList.add(savedTheme);
        });
        themeIcon.textContent = savedTheme === 'dark' ? '🌙' : '☀️';
    } else {
        document.body.classList.add('light'); // Default to light theme
        navbar.classList.add('light');
        tables.forEach(table => {
            table.classList.add('light');
        });
        themeIcon.textContent = '☀️';
    }
};
