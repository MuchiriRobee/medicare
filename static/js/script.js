// Add fade-in animation to elements with the class 'fade-in'
document.addEventListener('DOMContentLoaded', () => {
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.transition = 'opacity 1s ease-in-out';
            element.style.opacity = '1';
        }, 100);
    });
});

// Add slide-in animation to elements with the class 'slide-in'
document.addEventListener('DOMContentLoaded', () => {
    const slideElements = document.querySelectorAll('.slide-in');
    slideElements.forEach(element => {
        element.style.transform = 'translateY(20px)';
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.transition = 'transform 0.5s ease-in-out, opacity 0.5s ease-in-out';
            element.style.transform = 'translateY(0)';
            element.style.opacity = '1';
        }, 100);
    });
});

// Form Validation for Booking Page
document.querySelector('form').addEventListener('submit', (event) => {
    const fullName = document.getElementById('full_name').value.trim();
    const phoneNumber = document.getElementById('phone_number').value.trim();
    const email = document.getElementById('email').value.trim();
    const appointmentDate = document.getElementById('appointment_date').value.trim();

    if (!fullName || !phoneNumber || !email || !appointmentDate) {
        event.preventDefault();
        alert('Please fill out all required fields.');
    }
});

// Toggle Mobile Navigation Menu
const navToggle = document.createElement('button');
navToggle.innerHTML = '&#9776;';
navToggle.classList.add('nav-toggle');
document.querySelector('header').appendChild(navToggle);

navToggle.addEventListener('click', () => {
    const nav = document.querySelector('nav ul');
    nav.classList.toggle('active');
});

// Smooth Scrolling for Anchor Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});
// Contact Form Submission
document.getElementById('contactForm').addEventListener('submit', (event) => {
    event.preventDefault();
    alert('Thank you for your message! We will get back to you soon.');
    event.target.reset();
});
// Add fade-in animation to elements with the class 'fade-in'
document.addEventListener('DOMContentLoaded', () => {
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.transition = 'opacity 1s ease-in-out';
            element.style.opacity = '1';
        }, 100);
    });
});

// Add slide-in animation to elements with the class 'slide-in'
document.addEventListener('DOMContentLoaded', () => {
    const slideElements = document.querySelectorAll('.slide-in');
    slideElements.forEach(element => {
        element.style.transform = 'translateY(20px)';
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.transition = 'transform 0.5s ease-in-out, opacity 0.5s ease-in-out';
            element.style.transform = 'translateY(0)';
            element.style.opacity = '1';
        }, 100);
    });
});

// Highlight table rows on hover
document.addEventListener('DOMContentLoaded', () => {
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = '#f1f1f1';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = 'white';
        });
    });
});
// Services Section - Category Filtering
document.addEventListener('DOMContentLoaded', () => {
    const categoryButtons = document.querySelectorAll('.category-btn');
    const serviceCategories = document.querySelectorAll('.service-category');
    
    // Add click event listeners to category buttons
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active button
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const selectedCategory = button.getAttribute('data-category');
            
            if (selectedCategory === 'all') {
                // Show all categories
                serviceCategories.forEach(category => {
                    category.style.display = 'block';
                });
            } else {
                // Show only selected category, hide others
                serviceCategories.forEach(category => {
                    if (category.id === selectedCategory) {
                        category.style.display = 'block';
                    } else {
                        category.style.display = 'none';
                    }
                });
            }
        });
    });
    
    // Book appointment buttons - scroll to appointments section
    const bookButtons = document.querySelectorAll('.service-card a');
    
    bookButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Get the service name from the parent card
            const serviceCard = button.closest('.service-card');
            const serviceName = serviceCard.querySelector('h4').textContent;
            
            // Store selected service in session storage
            sessionStorage.setItem('selectedService', serviceName);
            
            // Scroll to appointments section
            document.getElementById('appointments').scrollIntoView({ behavior: 'smooth' });
            
            // Trigger set appointment button click after scrolling
            setTimeout(() => {
                document.getElementById('set-appointment-btn').click();
            }, 1000);
        });
    });
});
// JavaScript for FAQ accordions
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const item = question.parentNode;
        item.classList.toggle('active');
    });
});
// Get the modal and close button
const modal = document.getElementById('confirmationModal');
const closeBtn = document.querySelector('.close');

// Function to show the modal
function showModal() {
    modal.style.display = 'block';
}

// Function to hide the modal
function hideModal() {
    modal.style.display = 'none';
}

// Close the modal when the close button is clicked
closeBtn.addEventListener('click', hideModal);

// Close the modal when clicking outside the modal
window.addEventListener('click', (event) => {
    if (event.target === modal) {
        hideModal();
    }
});
// Show the modal if there's a success flash message
document.addEventListener('DOMContentLoaded', () => {
    const successMessage = document.querySelector('.alert-success');
    if (successMessage) {
        showModal();
    }
});

// Handle form submission
document.getElementById('bookingForm').addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent the default form submission

    // Get form data
    const formData = new FormData(event.target);

    // Convert form data to JSON
    const jsonData = {};
    formData.forEach((value, key) => {
        jsonData[key] = value;
    });

    // Submit form data using fetch()
    fetch('/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Set the correct Content-Type
        },
        body: JSON.stringify(jsonData), // Convert data to JSON
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show the modal on success
            showModal();
            // Reset the form
            event.target.reset();
        } else {
            alert('Failed to book appointment. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eyeIcon');
    
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      eyeIcon.innerHTML = '<path d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>';
    } else {
      passwordInput.type = 'password';
      eyeIcon.innerHTML = '<path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>';
    }
  }
  
  // Add animations to form elements on page load
  document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.login-container');
    container.style.opacity = '0';
    container.style.transform = 'translateY(20px)';
    
    setTimeout(function() {
      container.style.opacity = '1';
      container.style.transform = 'translateY(0)';
    }, 200);
  });
  // Toggle dropdown menu on click
document.addEventListener('DOMContentLoaded', function () {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    dropdownToggle.addEventListener('click', function (event) {
        event.preventDefault();
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });

    // Close dropdown when clicking outside
    window.addEventListener('click', function (event) {
        if (!event.target.matches('.dropdown-toggle')) {
            dropdownMenu.style.display = 'none';
        }
    });
});