document.addEventListener("DOMContentLoaded", function () {

    const flash = document.getElementById("flash-message");

    if (!flash) {
        return;
    }

    Swal.fire({
        icon: flash.dataset.icon,
        title: flash.dataset.title,
        text: flash.dataset.message,
        timer: 2500,
        timerProgressBar: true,
        showConfirmButton: false
    });

});