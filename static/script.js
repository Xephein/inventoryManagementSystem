function tableFilter() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("filterInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("toFilter");
    tr = table.getElementsByTagName("tr");

    console.log(filter);
  
    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
      tdname = tr[i].getElementsByTagName("td")[0];
      tditem = tr[i].getElementsByTagName("td")[1];
      console.log(tdname);
      console.log(tditem);
      if (tdname) {
        txtValue = tdname.textContent || tdname.innerText;
        itemValue = tditem.textContent || tditem.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1 || itemValue.toUpperCase().indexOf(filter) > -1)  {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }