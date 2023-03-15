// Send the purchasing department's email and password for authentication
const submitCredentials = () => {
  const emailAddress = document.getElementById("emailField");
  const password = document.getElementById("passwordField");
  const submitButton = document.getElementById("submitCredentialsBtn");
  const statusText = document.getElementById("statusText");

  if (emailAddress.value === "" || password.value === "") {
    statusText.innerHTML = "Missing email address or password";
  } else {
    statusText.innerHTML = "";
    submitButton.textContent = "Credentials submitted";
    submitButton.disabled = true;
  }
};
