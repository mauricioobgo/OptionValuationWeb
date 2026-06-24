$(document).ready(function () {
  let optionTypesSelected = [];
  let optionLabelsSelected = [];
  let chartInstance = null;

  $.ajax({
    url: "/process",
    type: "GET",
    success: function (response) {
      response.option_type.forEach(function (label, index) {
        $("#option_type").append(
          `<option value="${index + 1}">${label}</option>`
        );
      });
    },
  });

  $("#option_type").on("change", function () {
    optionTypesSelected = [];
    optionLabelsSelected = [];
    $("option:selected", this).each(function () {
      optionTypesSelected.push(parseInt($(this).val()));
      optionLabelsSelected.push($(this).text().trim());
    });
  });

  $("#reset_form").click(function () {
    location.reload();
  });

  $("#make_calulation").click(function (event) {
    event.preventDefault();

    if (optionTypesSelected.length === 0 || $("#option_node_calc").val() === "") {
      alert("Please select an option type and fill in all required fields.");
      return;
    }

    var payload = {
      option_types: optionTypesSelected,
      spot: parseFloat($("#option_spot").val()),
      strike: parseFloat($("#option_strike").val()),
      rate: parseFloat($("#option_rate").val()),
      volatility: parseFloat($("#option_sd_risk").val()),
      time_days: parseFloat($("#option_time_years").val()),
      nodes: parseInt($("#option_node_calc").val()),
    };

    $.ajax({
      url: "/option_calculation",
      type: "POST",
      data: JSON.stringify(payload),
      contentType: "application/json; charset=UTF-8",
      success: function (data_response) {
        var results = data_response.finalValue;
        var values = optionTypesSelected.map((id) => results[String(id)]);

        $("#option_value_result").attr("style", "visibility: visible;");
        $("#results_adding").empty();

        if (chartInstance) {
          chartInstance.destroy();
        }
        chartInstance = new Chart($("#myChart"), {
          type: "bar",
          data: {
            labels: optionLabelsSelected,
            datasets: [{ label: "Option Prices", data: values }],
          },
          options: {
            scales: {
              yAxes: [{ ticks: { beginAtZero: true } }],
            },
          },
        });

        optionLabelsSelected.forEach(function (label, i) {
          $("#results_adding").append(
            `<tr><td>${label}</td><td>${values[i]}</td></tr>`
          );
        });
      },
      error: function (xhr) {
        alert("Calculation failed: " + (xhr.responseJSON?.detail || xhr.responseText));
      },
    });
  });
});
