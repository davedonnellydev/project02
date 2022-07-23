const searchBar = document.getElementById("movieSearch");

searchBar.addEventListener("keyup", search);

function search() {
  searchTerm = searchBar.value;
  console.log(searchTerm);
}
