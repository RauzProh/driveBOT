let token = null;

// document.getElementById("loginForm").addEventListener("submit", async (e) => {
//   e.preventDefault();
//   const username = document.getElementById("username").value;
//   const password = document.getElementById("password").value;

//   const formData = new URLSearchParams();
//   formData.append("username", username);
//   formData.append("password", password);
//     console.log(formData.toString());
//   const res = await fetch("/token", {
//     method: "POST",
//     headers: { "Content-Type": "application/x-www-form-urlencoded" },
//     body: formData.toString(),
//   });

//   const data = await res.json();
//   if (data.access_token) {
//     token = data.access_token;
//     document.getElementById("result").innerText = "Logged in! Token: " + token;
//   } else {
//     document.getElementById("result").innerText = "Error: " + data.error;
//   }
// });

// async function getSecure() {
//   const res = await fetch("/secure-data", {
//     headers: { Authorization: `Bearer ${token}` },
//   });
//   const data = await res.json();
//   document.getElementById("result").innerText = JSON.stringify(data);
// }

async function getSecure() {
  console.log("Token being sent:", token); // <--- добавь
  const restt = await createOrder("Test Order", token);
  const orders = await getOrders(token);
  console.log(orders);
  console.log("Create Order Response:", restt); // <--- добавь
  const res = await fetch("/secure-data", {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  document.getElementById("result").innerText = JSON.stringify(data);
}

async function getOrders(token) {
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


async function createOrder(orderName, token) {
  try {
    // Формируем данные для отправки
    const formData = new URLSearchParams();
    formData.append("order_name", orderName);

    // Делаем POST-запрос
    const response = await fetch("/create-order", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`, // токен пользователя
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: formData
    });

    // Получаем JSON с результатом
    const data = await response.json();

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

function updateLeft() {
    console.log('Updating left position');
    const screenWidth = window.innerWidth; // ширина экрана
    const blockWidth = block.offsetWidth;   // ширина блока
    block.style.position = 'absolute';      // обязательно absolute
    block.style.left = `${screenWidth / 2 - blockWidth / 2}px`; // центрирование
  }

  // запуск при загрузке страницы
  updateLeft();

  // запуск при изменении размера окна
  window.addEventListener('resize', updateLeft);