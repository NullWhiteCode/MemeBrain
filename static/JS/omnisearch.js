console.log("omnisearch.js loaded");

const searchForm = document.querySelector(".search-bar");
const searchButton = document.querySelector(".search-button");

function handleSearchSubmit() {
    console.log("OmniSearch submitted");
    searchButton.textContent="Praise the Omnissiah...";
}

searchForm.addEventListener("submit", handleSearchSubmit);