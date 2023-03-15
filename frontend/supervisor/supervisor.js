// Send the supervisor's email and password for authentication
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

// Get list of incoming orders
// TODO: determine how multiple orders from users are handled
const fetchIncomingOrders = () => {
  console.log("Orders fetched!");
};

// Sign off on the incoming request
// TODO: do we have a "sign off" button for each incoming order?
// If we're handling multiple orders in our app, maybe we remove the incoming
// order and button once that specific order has been signed off on?
const onSignOff = () => {
  console.log("Signed off on order");
};
