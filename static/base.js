function removeFlashMessages() {
    var flashMessages = document.querySelectorAll('.flash-messages li');
    flashMessages.forEach(function (message) {
      setTimeout(function () {
        message.remove();
      }, 5000); // Adjust the time (in milliseconds) as needed, e.g., 5000 for 5 seconds
    });
  }

  // Call the function when the page has finished loading
  window.addEventListener('load', removeFlashMessages);