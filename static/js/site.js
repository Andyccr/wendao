(function () {
  var toggle = document.getElementById("nav-toggle");
  var drawer = document.getElementById("drawer");
  var mask = document.getElementById("drawer-mask");
  if (!toggle || !drawer || !mask) return;

  function setOpen(open) {
    drawer.classList.toggle("is-open", open);
    mask.classList.toggle("is-open", open);
    document.body.classList.toggle("drawer-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "关闭菜单" : "打开菜单");
  }

  toggle.addEventListener("click", function () {
    setOpen(!drawer.classList.contains("is-open"));
  });
  mask.addEventListener("click", function () {
    setOpen(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") setOpen(false);
  });
})();
