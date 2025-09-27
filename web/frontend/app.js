let token = null;

document.addEventListener("DOMContentLoaded", async () => {
  const overlay = document.getElementById("loginOverlay");

  if (!(await isTokenActive())) {
    overlay.style.display = "flex"; 
    return;
  }

  const path = window.location.pathname;
  if (path === "/drivers") {
    renderDrivers();
  } else if (path === "/") {
    renderOrders();
    renderSuppliersForOrder()
    renderSuppliersForDetails()
    renderDriversForDetails()
  } else if (path === "/suppliers") {
    renderSuppliers();
  }
});

document.addEventListener("DOMContentLoaded", async () => {
  const path = window.location.pathname;
  if (path === "/drivers") {

  } else if (path === "/suppliers") {
    document.getElementById("supplieForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const suplier = Object.fromEntries(formData.entries());
    console.log("Новый поставщик:", suplier);
    // createOrder(order);
    createSupplier(suplier);

    // TODO: отправка на сервер через fetch("/create-order", {method:"POST", body: JSON.stringify(order)})
    
    alert("Поставщик добавлен!");
    closeSupplier();
    renderSuppliers()
    // renderOrders(); // обновляем список заказов
    // Очищаем форму
    form.reset();
    });

  }else if (path === "/") {
        // запуск при загрузке страницы
    updateLeft();

    // запуск при изменении размера окна
    window.addEventListener('resize', updateLeft);

    // Делегирование кликов на контейнер
    container.addEventListener("click", (event) => {
    const card = event.target.closest(".trip-card");
    if (!card) return; // Клик вне карточки — игнорируем

    if (event.target.classList.contains("cancelbtn")) {
        // Клик по кнопке отмены
        const orderId = card.dataset.orderId;
        cancelOrder(orderId);
        renderOrders();
    } else {
        // Клик по карточке (не кнопка)
        const orderId = card.dataset.orderId;
        DetailsOpen(orderId)
        console.log("Клик на карточку, orderId:", orderId);
        // showOrderDetails(orderId);
    }
    });



    // обработка формы
    document.getElementById("orderForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const order = Object.fromEntries(formData.entries());
    console.log("Новый заказ:", order);
    createOrder(order);

    // TODO: отправка на сервер через fetch("/create-order", {method:"POST", body: JSON.stringify(order)})
    
    alert("Заказ создан!");
    closeOrder();
    renderOrders(); // обновляем список заказов
    // Очищаем форму
    form.reset();
    });
    document.getElementById("orderDetailsForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const form = e.target;
    const order_id = form.dataset.id
    console.log(order_id)
    const formData = new FormData(form);
    const order = Object.fromEntries(formData.entries());
    order.id = parseInt(order_id);
    console.log("обновление заказа заказ:", order);
    updateOrder(order);
    closeDetails()

    // TODO: отправка на сервер через fetch("/create-order", {method:"POST", body: JSON.stringify(order)})
    
    alert("Заказ создан!");
    closeOrder();
    renderOrders(); // обновляем список заказов
    // Очищаем форму
    form.reset();
    });
  }
});





document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
    console.log(formData.toString());
  const res = await fetch("/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString(),
  });

  const data = await res.json();
//   if (data.access_token) {
//     token = data.access_token;
//     document.getElementById("result").innerText = "Logged in! Token: " + token;
//   } else {
//     document.getElementById("result").innerText = "Error: " + data.error;
//   }
    if (data.access_token) {
        localStorage.setItem("token", data.access_token); // сохраняем
        // document.getElementById("result").innerText = "Logged in!";
        document.getElementById("loginOverlay").style.display = "none"; // скрыть окно
        const path = window.location.pathname;
        if (path === "/drivers") {
            renderDrivers();
        } else if (path === "/") {
            renderOrders();
            renderSuppliersForOrder()
            renderSuppliersForDetails()
            renderDriversForDetails()
        } else if (path === "/suppliers") {
            renderSuppliers();
        }
        // alert("Успешный вход!");
    } else {
        alert("Неверный логин или пароль!");
    }
});

async function getSecure() {
  const res = await fetch("/secure-data", {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  document.getElementById("result").innerText = JSON.stringify(data);
}

async function isTokenActive() {
  const token = localStorage.getItem("token");
  if (!token) return false;

  try {
    const res = await fetch("/secure-data", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      return true; // токен жив
    } else {
      console.warn("Token invalid:", res.status);
      return false;
    }
  } catch (e) {
    console.error("Ошибка проверки токена:", e);
    return false;
  }
}

async function getOrders() {
     const token = localStorage.getItem("token");
    if (!token) {
        alert("Пожалуйста, войдите в систему.");
        return;
    }
  try {
    const response = await fetch("/getorders", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/json"
      }
    });

    const data = await response.json();

    if (response.ok) {
      console.log("Полученные заказы:", data.orders);
      return data.orders;
    } else {
      console.error("Ошибка при получении заказов:", data);
      return [];
    }
  } catch (error) {
    console.error("Ошибка запроса:", error);
    return [];
  }
}


async function createOrder(order) {
    const token = localStorage.getItem("token");
    console.log("Creating order with token:", token, "and order:", order); // <--- добавь
    if (!token) {
        alert("Пожалуйста, войдите в систему.");
        return;
    }

  try {
    const response = await fetch("/create-order", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`, // токен пользователя
        "Content-Type": "application/json"
      },
      body: JSON.stringify(order) // отправляем JSON, а не formData
    });

    const data = await response.json();
    console.log("Response from createOrder:", data);

    if (response.ok) {
      console.log("Заказ создан:", data);
    } else {
      console.error("Ошибка при создании заказа:", data);
    }

    return data;
  } catch (error) {
    console.error("Ошибка запроса:", error);
    return { status: "error", detail: error.message };
  }
}

async function updateOrder(order) {
    const token = localStorage.getItem("token");
    console.log("Creating order with token:", token, "and order:", order); // <--- добавь
    if (!token) {
        alert("Пожалуйста, войдите в систему.");
        return;
    }

  try {
    const response = await fetch("/update-order", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`, // токен пользователя
        "Content-Type": "application/json"
      },
      body: JSON.stringify(order) // отправляем JSON, а не formData
    });

    const data = await response.json();
    console.log("Response from updateOrder:", data);

    if (response.ok) {
      console.log("Заказ обновлен:", data);
    } else {
      console.error("Ошибка при обновлении заказа:", data);
    }

    return data;
  } catch (error) {
    console.error("Ошибка запроса:", error);
    return { status: "error", detail: error.message };
  }
}


async function createSupplier(supplier) {
    const token = localStorage.getItem("token");
    console.log("Creating order with token:", token, "and supplier:", supplier); // <--- добавь
    if (!token) {
        alert("Пожалуйста, войдите в систему.");
        return;
    }

  try {
    const response = await fetch("/create-supplier", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`, // токен пользователя
        "Content-Type": "application/json"
      },
      body: JSON.stringify(supplier) // отправляем JSON, а не formData
    });

    const data = await response.json();
    console.log("Response from createOrder:", data);

    if (response.ok) {
      console.log("Заказ создан:", data);
    } else {
      console.error("Ошибка при создании заказа:", data);
    }

    return data;
  } catch (error) {
    console.error("Ошибка запроса:", error);
    return { status: "error", detail: error.message };
  }
}


const block = document.querySelector('.trips-new-details_desktop');

async function DetailsOpen(id) {
    block.style.display = "flex";
    const orders = await getOrders()
    console.log(orders)
    console.log(orders[1])
    renderDetails(orders[parseInt(id)-1])
    
}

function closeDetails() {
  block.style.display = "none";
}

function updateLeft() {
    console.log('Updating left position');
    const screenWidth = window.innerWidth; // ширина экрана
    const blockWidth = block.offsetWidth;   // ширина блока
    block.style.position = 'absolute';      // обязательно absolute
    block.style.left = `${screenWidth / 2}px`; // центрирование
}



// const select = document.querySelector(".select-custom");
//   const placeholder = select.querySelector(".select-custom-link-display__placeholder");
//   const options = select.querySelectorAll(".option");

//   placeholder.addEventListener("click", () => {
//     select.classList.toggle("open");
//   });

//   options.forEach(option => {
//     option.addEventListener("click", () => {
//       placeholder.textContent = option.textContent;
//       select.classList.remove("open");
//     });
//   });

//   document.addEventListener("click", (e) => {
//     if (!select.contains(e.target)) {
//       select.classList.remove("open");
//     }
//   });


function createOrderOpen() {
  document.getElementById("orderOverlay").style.display = "flex";
}

function closeOrder() {
  document.getElementById("orderOverlay").style.display = "none";
}


function createSupplierOpen() {
  document.getElementById("supplierOverlay").style.display = "flex";
}

function closeSupplier() {
  document.getElementById("supplierOverlay").style.display = "none";
}





async function getDrivers() {
     const token = localStorage.getItem("token");
    if (!token) {
        alert("Пожалуйста, войдите в систему.");
        return;
    }
  try {
    const response = await fetch("/getdrivers", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/json"
      }
    });

    const data = await response.json();

    if (response.ok) {
      console.log("Полученные водители", data.drivers);
      return data.drivers;
    } else {
      console.error("Ошибка при получении заказов:", data);
      return [];
    }
  } catch (error) {
    console.error("Ошибка запроса:", error);
    return [];
  }
}

async function getSuppliers() {
     const token = localStorage.getItem("token");
    if (!token) {
        alert("Пожалуйста, войдите в систему.");
        return;
    }
  try {
    const response = await fetch("/getsuppliers", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/json"
      }
    });

    const data = await response.json();

    if (response.ok) {
      console.log("Полученные поставщики", data.suppliers);
      return data.suppliers;
    } else {
      console.error("Ошибка при получении заказов:", data);
      return [];
    }
  } catch (error) {
    console.error("Ошибка запроса:", error);
    return [];
  }
}



async function cancelOrder(orderId) {
    
  if (!confirm(`Вы точно хотите отменить заказ #${orderId}?`)) return;

  try {
    const token = localStorage.getItem("token");
    const resp = await fetch(`/cancel-order/${orderId}`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });
    const data = await resp.json();
    if (resp.ok) {
      alert("Заказ отменён");
      await renderOrders(); // обновляем список после отмены
    } else {
      alert("Ошибка при отмене: " + data.detail);
    }
  } catch (err) {
    console.error(err);
    alert("Ошибка запроса");
  }
}

async function renderOrders() {
  const orders = await getOrders();
  const drivers = await getDrivers();
  console.log(drivers)
  const container = document.querySelector(".trips-new-list");
  container.innerHTML = "";

  if (!orders || orders.length === 0) {
    container.innerHTML = "<div>Нет заказов</div>";
    return;
  }

  orders.sort((a, b) => new Date(b.scheduled_time) - new Date(a.scheduled_time));

  let prevDateKey = null;

  for (const order of orders) {
    const dt = new Date(order.scheduled_time);
    const dateKey = `${dt.getFullYear()}-${dt.getMonth()+1}-${dt.getDate()}`;

    if (dateKey !== prevDateKey) {
      prevDateKey = dateKey;
      const dateLabel = dt.toLocaleDateString("ru-RU", { day: "numeric", month: "long" });
      container.insertAdjacentHTML("beforeend", `<div class="trips-new-list-date">${dateLabel}</div>`);
    }

    const time = dt.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
    const fromText = order.from_address + (order.trip_number ? ` (${order.trip_number})` : "");
    const priceText = (order.price !== null && order.price !== undefined) ? `${order.price} ₽` : "—";
    const carClass = order.car_class || "—";
    const passenger = order.passenger_info || "—";
    const statusClass = order.status || "";
    const modeText = (order.mode === "fcfs") ? "FCFS" : (order.mode === "auction" ? "Auction" : order.mode);
    const driverid = order.driver_id || "—";
    console.log(order)
    console.log(drivers)
    const drivername = "-"
    if (order.driver_id) {
         drivername = drivers[order.driver_id-1].full_name
    }

    const cardHtml = `
      <div class="trip-card" data-order-id="${order.id}">
        <div class="fline">
          <div class="time">${time}</div>
          <div>
            <div class="order_info">
              <div>${carClass}</div>
              <div class="devinder"></div>
              <div class="price">${priceText}</div>
            </div>
            <div>${drivername}</div>
          </div>
          <div class="status ${statusClass}">${statusClass}</div>
          <div class="ordertype">Тип - ${modeText}</div>
          <div class="orderid">${order.price_0} ₽ | ${order.ordernumb}        #${order.id}</div>
        </div>
        <div class="card-adreses">
            <div class="from-text">Откуда:</div>
            <div class="from">${escapeHtml(fromText)}</div>
            <div class="to-text">Куда:</div>
            <div class="to">${escapeHtml(order.to_address || "Без водителя")}</div>
        </div>
        <div class="card-cancel-btn"><button class="cancelbtn">Отменить </button></div>
      </div>
    `;

    container.insertAdjacentHTML("beforeend", cardHtml);
  }

//   // Навешиваем обработчики на кнопки через отдельную функцию
//   container.querySelectorAll(".cancelbtn").forEach(btn => {
//     btn.addEventListener("click", () => {
//       const orderId = btn.closest(".trip-card").dataset.orderId;
//       cancelOrder(orderId);
//       renderOrders(); // обновляем список заказов
//     });
//   });
//   container.querySelectorAll(".trip-card").forEach(card => {
//   card.addEventListener("click", (event) => {
//     // Если клик не по кнопке
//     if (!event.target.classList.contains("cancelbtn")) {
//       const orderId = card.dataset.orderId;
//       console.log("Клик на карточку, orderId:", orderId);
//       // Здесь твоё действие при клике на карточку
//       showOrderDetails(orderId);
//     }
//   });
// });
}


const container = document.querySelector(".trips-new-list");




// простая защита от инъекций, если данные из внешнего источника
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}



// async function renderDrivers() {
//   const drivers = await getDrivers();
//   const list = document.querySelector(".drivers-list");
//   list.innerHTML = ""; // очистка

//   drivers.forEach(driver => {
//     const photo = driver.documents?.selfie || "placeholder.jpg";
//     const card = document.createElement("div");
//     card.className = "driver-card";

//     card.innerHTML = `
//       <div class="driver-photo">
//         <img src="${photo}" alt="Фото водителя">
//       </div>
//       <div class="driver-info">
//         <h3 class="driver-name">${driver.full_name || "Неизвестно"}</h3>
//         <p class="driver-phone">Телефон: ${driver.phone || "-"}</p>
//         <p class="driver-city">Город: ${driver.city || "-"}</p>
//         <p class="driver-car">
//           Авто: ${driver.car_brand || ""} 
//           ${driver.car_model || ""}, 
//           ${driver.car_color || ""}, 
//           ${driver.car_number || ""}
//         </p>
//         <p class="driver-rating">Рейтинг: ${driver.rating ?? "нет данных"}</p>
//         <p class="driver-orders">
//           Выполнено: ${driver.completed_orders} | Отменено: ${driver.cancelled_orders}
//         </p>
//       </div>
//     `;

//     list.appendChild(card);
//   });
// }


async function renderDrivers() {
  const drivers = await getDrivers();
  const list = document.querySelector(".drivers-list");
  list.innerHTML = ""; // очистка

  drivers.forEach(driver => {
    const photo = driver.documents?.selfie || "placeholder.jpg";
    const card = document.createElement("div");
    card.className = "driver-card";

    card.innerHTML = `
      <div class="driver-photo">
        <img src="driverphoto" alt="Фото водителя">
      </div>
      <div class="driver-info">
        <h3 class="driver-name">${driver.full_name || "Неизвестно"}</h3>
        <p class="driver-phone">Телефон: ${driver.phone || "-"}</p>
        <p class="driver-city">Регион: ${driver.city || "-"}</p>
        <p class="driver-car">
          Авто: ${driver.car_brand || ""} 
          ${driver.car_model || ""}, 
          ${driver.car_color || ""}, 
          ${driver.car_number || ""}
        </p>
      </div>
    `;

    list.appendChild(card);
  });
}
async function renderSuppliers() {
  const suppliers = await getSuppliers();
  const list = document.querySelector(".suppliers-list");
  list.innerHTML = ""; // очистка

  suppliers.forEach(driver => {
    const name = driver.name
    const card = document.createElement("div");
    card.className = "supplier-card";

    card.innerHTML = `
      <div>
            ${driver.name || ""}
      </div>
    `;

    list.appendChild(card);
  });
}
async function renderSuppliersForOrder() {
  const suppliers = await getSuppliers();
  const form = document.getElementById("orderForm");
  if (!form) return;

  const select = form.querySelector('select[name="supplier"]');
  if (!select) return;

  select.innerHTML = '<option value="" disabled selected>Выберите поставщика</option>';

  suppliers.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    select.appendChild(opt);
  });
}

async function renderSuppliersForDetails() {
  const suppliers = await getSuppliers();
  const form = document.getElementById("orderDetailsForm");
  if (!form) return;

  const select = form.querySelector('select[name="supplier"]');
  if (!select) return;

  select.innerHTML = '<option value="" disabled selected>Выберите поставщика</option>';

  suppliers.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    select.appendChild(opt);
  });
}

async function renderDriversForDetails() {
  const suppliers = await getDrivers();
  const form = document.getElementById("orderDetailsForm");
  if (!form) return;

  const select = form.querySelector('select[name="driver"]');
  if (!select) return;

  select.innerHTML = '<option value="" disabled selected>None</option>';

  suppliers.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.full_name;
    select.appendChild(opt);
  });
}


async function renderDetails(order) {
    if (!order || typeof order !== "object") {
    console.warn("renderDetails получил пустой order:", order);
    return;
  }
  const form = document.getElementById("orderDetailsForm");
  form.dataset.id = order.id
  if (!form) return;

  const mapping = {
    ordernumb: "ordernumb",
    city: "region",
    supplier_id: "supplier",
    from_address: "from",
    to_address: "to",
    scheduled_time: "datetime",
    car_class: "car_class",
    price_0: "price_0",
    price: "price",
    mode: "mode",
    trip_number: "flight",
    comments: "comment",
    passenger_info: "contact",
    supplier: "supplier_id"
  };

  for (const [key, fieldName] of Object.entries(mapping)) {
    const field = form.elements[fieldName];
    if (!field) continue;
    if(key==='supplier_id') {
        console.log(fieldName)
        console.log(key)
        console.log(order)
        console.log(order[key])
    }
    let value = order[key];

    // спец-обработка для datetime-local
    if (field.type === "datetime-local" && value) {
      // отрезаем секунды и Z если есть
      value = value.slice(0, 16);
    }

    field.value = value ?? "";
  }
}