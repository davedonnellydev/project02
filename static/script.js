const addMovieButton = document.getElementById("movieSearchButton");
const searchMoviesForm = document.getElementById("movieSearchForm");

addMovieButton.addEventListener("click", revealSearchForm);

function revealSearchForm() {
  searchMoviesForm.style.display = "block";
}
