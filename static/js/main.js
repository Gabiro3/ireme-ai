document.querySelectorAll('.toggle-password').forEach(function(togglePasswordIcon) {
    togglePasswordIcon.addEventListener('click', function() {
        const input = this.previousElementSibling;
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        this.classList.toggle('bi bi-eye');
        this.classList.toggle('bi bi-eye-slash');
    });
  });
      
  
      // script.js 
  
    // Get the snackbar DIV
    var x = document.getElementById("snackbar");
  
    // Add the "show" class to DIV
    x.className = "show";
  
    // After 3 seconds, remove the show class from DIV
    setTimeout(function(){ x.className = x.className.replace("show", ""); }, 5000);