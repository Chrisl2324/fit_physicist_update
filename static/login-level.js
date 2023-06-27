console.log("login-level.js file loaded");

$(document).ready(function () {
  $("#login-button").click(function (event) {
    event.preventDefault();


    var username = $("#login-username").val();
    var password = $("#login-password").val();

    console.log("Username:", username);
    console.log("Password:", password);

   
    if (!username || !password) {
      alert("Please fill in all fields");
      return;
    }

    $.ajax({
      url: "/",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        username: username,
        password: password,
      }),
      success: function () {
        alert("Login successful!");
        location.reload();
      },
      error: function (xhr) {
        var response = JSON.parse(xhr.responseText);
        alert("Login failed: " + response.message);
      },
    });
  });
});
