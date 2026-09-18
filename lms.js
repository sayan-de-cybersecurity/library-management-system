// ==========================================
// LIBRARY MANAGEMENT SYSTEM FRONTEND
// ==========================================


// ================= THEME =================

function toggleTheme() {

    document.body.classList.toggle("dark");

    const darkMode =
        document.body.classList.contains("dark");

    localStorage.setItem(
        "libraryTheme",
        darkMode ? "dark" : "light"
    );

}


// Load saved theme

document.addEventListener("DOMContentLoaded", function () {

    const savedTheme =
        localStorage.getItem("libraryTheme");

    if (savedTheme === "dark") {
        document.body.classList.add("dark");
    }

});


// ================= BOOK SEARCH =================

function searchBooks() {

    const searchInput =
        document.getElementById("bookSearch");

    const search =
        searchInput.value.toLowerCase();

    const books =
        document.querySelectorAll(".book-card");

    books.forEach(function (book) {

        const text =
            book.innerText.toLowerCase();

        if (text.includes(search)) {

            book.style.display = "";

        } else {

            book.style.display = "none";

        }

    });

}


// ================= CATEGORY FILTER =================

function filterBooks() {

    const category =
        document.getElementById("categoryFilter").value;

    const books =
        document.querySelectorAll(".book-card");

    books.forEach(function (book) {

        const bookCategory =
            book.dataset.category;

        if (
            category === "all" ||
            bookCategory === category
        ) {

            book.style.display = "";

        } else {

            book.style.display = "none";

        }

    });

}


// ================= BOOK MODAL =================

function showBook(bookName) {

    const modal =
        document.getElementById("bookModal");

    const name =
        document.getElementById("modalBookName");

    name.innerText = bookName;

    modal.classList.add("show");

}


// Close modal

function closeModal() {

    document
        .getElementById("bookModal")
        .classList.remove("show");

}


// Close modal when clicking outside

window.addEventListener("click", function (event) {

    const modal =
        document.getElementById("bookModal");

    if (event.target === modal) {

        closeModal();

    }

});


// ================= SMOOTH SCROLL =================

document.querySelectorAll('a[href^="#"]').forEach(
    function (link) {

        link.addEventListener("click", function (event) {

            const target =
                document.querySelector(
                    this.getAttribute("href")
                );

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth"
                });

            }

        });

    }
);