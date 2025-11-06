// Scroll reveal effect
document.addEventListener("scroll", () => {
  const reveals = document.querySelectorAll(".reveal");
  const windowHeight = window.innerHeight;
  reveals.forEach((el) => {
    const elementTop = el.getBoundingClientRect().top;
    if (elementTop < windowHeight - 100) {
      el.classList.add("active");
    }
  });
});

const response = await fetch("{% url 'dashboard_stats' %}", {
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin'
});
