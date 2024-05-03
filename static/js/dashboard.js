const search = document.querySelector('.input-group input'),
    table_rows = document.querySelectorAll('tbody tr'),
    table_headings = document.querySelectorAll('thead th');


function searchTable() {
    table_rows.forEach((row, i) => {
        let table_data = row.textContent.toLowerCase(),
            search_data = search.value.toLowerCase();

        row.classList.toggle('hide', table_data.indexOf(search_data) < 0);
        row.style.setProperty('--delay', i / 25 + 's');
    })

    document.querySelectorAll('tbody tr:not(.hide)').forEach((visible_row, i) => {
        visible_row.style.backgroundColor = (i % 2 == 0) ? 'transparent' : '#0000000b';
    });
}

// Sorting | Ordering data of HTML table

table_headings.forEach((head, i) => {
    let sort_asc = true;
    head.onclick = () => {
        table_headings.forEach(head => head.classList.remove('active'));
        head.classList.add('active');

        document.querySelectorAll('td').forEach(td => td.classList.remove('active'));
        table_rows.forEach(row => {
            row.querySelectorAll('td')[i].classList.add('active');
        })

        head.classList.toggle('asc', sort_asc);
        sort_asc = head.classList.contains('asc') ? false : true;

        sortTable(i, sort_asc);
    }
})


function sortTable(column, sort_asc) {
    [...table_rows].sort((a, b) => {
        let first_row = a.querySelectorAll('td')[column].textContent.toLowerCase(),
            second_row = b.querySelectorAll('td')[column].textContent.toLowerCase();

        return sort_asc ? (first_row < second_row ? 1 : -1) : (first_row < second_row ? -1 : 1);
    })
        .map(sorted_row => document.querySelector('tbody').appendChild(sorted_row));
}

// Select all elements with the class "searchIcon"
const searchIcons = document.querySelectorAll(".searchIcon");

// Loop through each search icon and attach event listeners
searchIcons.forEach(function (searchIcon) {
    searchIcon.addEventListener('click', function () {
        const parent = searchIcon.parentNode;
        const grnd_parent = searchIcon.parentNode.parentNode;
        const user_email = document.getElementById("email").innerText;
        const user_gender = document.getElementById("gender").innerText;
        const match_email = grnd_parent.childNodes[3].innerText;

        const data = {
            "m_email": user_gender === "Male" ? user_email : match_email,
            "f_email": user_gender === "Female" ? user_email : match_email,
        };

        $('#loading-overlay').show();

        $.ajax({
            url: "/get_score",
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                const { result_color, score } = response;
                parent.innerHTML = `<p class="${result_color}">${score}</p>`;
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("Error fetching score:", errorThrown);
            },
            complete: function () {
                // After the request is complete, hide the loading overlay
                $('#loading-overlay').hide();
            }
        });
    });
});
