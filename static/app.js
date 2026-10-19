"use strict";

const FRUITS = [
  { type: "white_peach", name: "White Peach", emoji: "🍑", price: 3.5 },
  { type: "red_apple", name: "Red Apple", emoji: "🍎", price: 2.0 },
  { type: "watermelon", name: "Watermelon", emoji: "🍉", price: 5.0 },
];

const API_BASE = "";

const stockList = document.getElementById("stock-list");
const fruitInputs = document.getElementById("fruit-inputs");
const totalEl = document.getElementById("total");
const messageEl = document.getElementById("message");
const ordersList = document.getElementById("orders-list");

function formatMoney(amount) {
  return "$" + Number(amount).toFixed(2);
}

function showMessage(text, type) {
  messageEl.textContent = text;
  messageEl.className = "message visible " + type;
  setTimeout(() => {
    messageEl.className = "message";
    messageEl.textContent = "";
  }, 6000);
}

async function loadInventory() {
  try {
    const res = await fetch(`${API_BASE}/inventory`);
    if (!res.ok) throw new Error("Failed to load inventory");
    const inventory = await res.json();

    stockList.innerHTML = "";
    inventory.forEach((item) => {
      const fruit = FRUITS.find((f) => f.type === item.fruit_type);
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <span class="emoji">${fruit ? fruit.emoji : "🍏"}</span>
        <div class="name">${fruit ? fruit.name : item.fruit_type}</div>
        <div class="stock">${item.quantity} in stock</div>
        <div class="stock">${formatMoney(item.unit_price)} each</div>
      `;
      stockList.appendChild(card);
    });
  } catch (err) {
    showMessage(err.message, "error");
  }
}

function renderInputs() {
  fruitInputs.innerHTML = "";
  FRUITS.forEach((fruit) => {
    const row = document.createElement("div");
    row.className = "fruit-row";
    row.innerHTML = `
      <div class="fruit-info">
        <span class="emoji">${fruit.emoji}</span>
        <div class="details">
          <span class="name">${fruit.name}</span>
          <span class="price">${formatMoney(fruit.price)} each</span>
        </div>
      </div>
      <input
        type="number"
        id="qty-${fruit.type}"
        min="0"
        max="20"
        value="0"
        data-type="${fruit.type}"
        data-price="${fruit.price}"
        aria-label="Quantity of ${fruit.name}"
      />
    `;
    fruitInputs.appendChild(row);
  });

  document.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener("input", updateTotal);
  });
}

function updateTotal() {
  let total = 0;
  document.querySelectorAll('input[type="number"]').forEach((input) => {
    const qty = Math.min(Math.max(parseInt(input.value, 10) || 0, 0), 20);
    input.value = qty;
    total += qty * parseFloat(input.dataset.price);
  });
  totalEl.textContent = formatMoney(total);
}

function getOrderPayload() {
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const address = document.getElementById("address").value.trim();

  if (!name || !phone || !address) {
    throw new Error("Please fill in all customer fields.");
  }

  const items = [];
  document.querySelectorAll('input[type="number"]').forEach((input) => {
    const qty = parseInt(input.value, 10) || 0;
    if (qty > 0) {
      items.push({
        fruit_type: input.dataset.type,
        quantity: Math.min(qty, 20),
      });
    }
  });

  if (items.length === 0) {
    throw new Error("Please select at least one fruit.");
  }

  return {
    customer: { name, phone, address },
    items,
  };
}

async function placeOrder() {
  try {
    const payload = getOrderPayload();
    const res = await fetch(`${API_BASE}/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Order failed");
    }

    showMessage(
      `Order confirmed! ID: ${data.order_id}. Total: ${formatMoney(data.total_amount)}`,
      "success"
    );

    // Reset form
    document.querySelectorAll('input[type="number"]').forEach((input) => {
      input.value = 0;
    });
    updateTotal();
    await loadInventory();
    await loadOrders();
  } catch (err) {
    showMessage(err.message, "error");
  }
}

function renderOrder(order) {
  const items = order.items
    .map(
      (item) =>
        `<li>${item.quantity} × ${item.fruit_type} @ ${formatMoney(
          item.unit_price
        )} = ${formatMoney(item.subtotal)}</li>`
    )
    .join("");

  return `
    <div class="order-card">
      <h3>Order #${order.order_id} — ${order.status}</h3>
      <div class="meta">${order.customer.name} | ${order.customer.phone}</div>
      <div class="meta">${order.customer.address}</div>
      <ul>${items}</ul>
      <div class="meta"><strong>Total: ${formatMoney(
        order.total_amount
      )}</strong> • ${new Date(order.created_at).toLocaleString()}</div>
    </div>
  `;
}

async function loadOrders() {
  try {
    const res = await fetch(`${API_BASE}/orders`);
    if (!res.ok) throw new Error("Failed to load orders");
    const orders = await res.json();

    if (orders.length === 0) {
      ordersList.innerHTML = '<p class="empty">No orders yet.</p>';
      return;
    }

    ordersList.innerHTML = orders
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .map(renderOrder)
      .join("");
  } catch (err) {
    ordersList.innerHTML = '<p class="empty">Could not load orders.</p>';
  }
}

document.getElementById("place-order").addEventListener("click", placeOrder);
document
  .getElementById("refresh-orders")
  .addEventListener("click", loadOrders);

// Initialize
loadInventory();
renderInputs();
updateTotal();
loadOrders();
