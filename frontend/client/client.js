// Send the client's email and password for authentication
const submitCredentials = () => {
  const emailAddress = document.getElementById("emailField");
  const password = document.getElementById("passwordField");
  const submitButton = document.getElementById("submitCredentialsButton");
};

// Submit an order
const submitOrder = () => {
  const item = document.getElementById("items").value;
  const submitButton = document.getElementById("submitOrderBtn");
  submitButton.textContent = "Order submitted";
  submitButton.disabled = true;
  console.log(item);
};
