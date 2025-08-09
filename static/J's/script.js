function showSection(id) {
    document.querySelectorAll(".section").forEach(sec => sec.classList.add("hidden"));
    document.getElementById(id).classList.remove("hidden");
}
