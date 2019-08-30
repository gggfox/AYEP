//Delete Confirmation
const btnDelete = document.querySelectorAll(".btn-delete");
if (btnDelete) {
    const btnarray = Array.from(btnDelete);
    btnarray.forEach((btn) => {
        btn.addEventListener("click", (e) => {
            if (!confirm("Are you sure you want to delete it?")) {
                e.preventDefault();
            }
        });
    });
}