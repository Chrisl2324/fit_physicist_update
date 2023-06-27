console.log("signup-level.js file loaded");

$(document).ready(function () {
  $("#terms").change(function () {
    if (this.checked) {
      $("#signup-button").prop("disabled", false);
    } else {
      $("#signup-button").prop("disabled", true);
    }
  });

  $("#signup-button").click(function (event) {
    event.preventDefault();

    // Get form values
    var username = $("#username").val();
    var firstName = $("#first_name").val();
    var lastName = $("#last_name").val();
    var email = $("#email").val();
    var password = $("#password").val();
    var confirmPassword = $("#confirm-password").val();
    var terms = $("#terms").prop("checked");

    // Validate form values
    if (!username || !firstName || !lastName || !email || !password || !confirmPassword) {
      alert("Please fill in all fields");
      return;
    }

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    if (!terms) {
      alert("Please agree to the Terms of Service");
      return;
    }

    // Make an AJAX request to the server
    $.ajax({
      url: "/",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        username: username,
        first_name: firstName,
        last_name: lastName,
        email: email,
        password: password,
      }),
      success: function () {
        alert("Sign up successful!");
        location.reload();
      },
      error: function (xhr) {
        var response = JSON.parse(xhr.responseText);
        alert("Sign up failed: " + response.message);
      },
    });
  });
});
