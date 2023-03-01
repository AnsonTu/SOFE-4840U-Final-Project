// Submit an order
const submitOrder = () => {
  const item = document.getElementById("items").value;
  const submitButton = document.getElementById("submitOrderBtn");
  submitButton.textContent = "Order submitted";
  submitButton.disabled = true;
  console.log(item);
};
