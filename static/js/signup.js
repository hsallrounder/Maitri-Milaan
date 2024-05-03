document.addEventListener("DOMContentLoaded", function() {
    const searchIcon = document.getElementById("searchIcon");
    const suggestionsDropdown = document.getElementById("suggestionsDropdown");
    const inputBox = document.querySelector(".input-box");
    const inputCity = document.getElementById("pob");
    const loader = document.getElementById("loader");
    let optionSelected = false; // Flag to track if an option has been selected
    let selectedOptionValue = ''; // Variable to store the selected option value

    searchIcon.addEventListener("click", function() {
        suggestionsDropdown.style.display = suggestionsDropdown.style.display === "block" ? "none" : "block";
        
        suggestionsDropdown.innerHTML = ""; // Clear previous suggestions

        const inputValue = inputCity.value.trim();

        if (inputValue.length > 0) {
            loader.style.display = "block"; // Show loader

            // Make an AJAX request to fetch suggestions
            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/get_sug", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    loader.style.display = "none"; // Hide loader

                    if (xhr.status === 200) {
                        const suggestionsData = JSON.parse(xhr.responseText);
                        displaySuggestions(suggestionsData);
                    } else {
                        console.error("Error fetching suggestions:", xhr.status);
                    }
                }
            };
            xhr.send("pob=" + inputValue);
        } else {
            suggestionsDropdown.style.display = "none";
        }
    });

    function displaySuggestions(suggestionsData) {
        // Display suggestions
        suggestionsData.forEach(function(item) {
            const suggestionItem = document.createElement("div");
            suggestionItem.textContent = `${item.city}, ${item.state}, ${item.country}`;
            suggestionsDropdown.appendChild(suggestionItem);

            // Handle click on suggestion item
            suggestionItem.addEventListener("click", function() {
                inputCity.value = item.city+", "+item.state+", "+item.country; // Set input value to clicked suggestion
                suggestionsDropdown.style.display = "none"; // Hide dropdown
                optionSelected = true; // Set the flag to true when an option is selected
                selectedOptionValue = inputCity.value; // Store the selected option value
            });
        });
    }

    // Close dropdown when clicking outside of it
    document.addEventListener("click", function(event) {
        if (!inputBox.contains(event.target) && event.target !== searchIcon) {
            suggestionsDropdown.style.display = "none";
        }
    });

    // Prevent closing dropdown when clicking on the search icon
    searchIcon.addEventListener("click", function(event) {
        event.stopPropagation();
    });

    // Submit handler
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        if (!optionSelected || inputCity.value !== selectedOptionValue) {
            alert('Please select POB from the options.'); // Display a message if no option is selected or the final value is different
            event.preventDefault(); // Prevent form submission
        }
    });
});
