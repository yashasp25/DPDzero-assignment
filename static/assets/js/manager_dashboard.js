document.addEventListener("DOMContentLoaded", function () {
  const sentimentData = document.getElementById("sentiment-data");

  const positive = parseInt(sentimentData.dataset.positive);
  const neutral = parseInt(sentimentData.dataset.neutral);
  const negative = parseInt(sentimentData.dataset.negative);

  const ctx = document.getElementById("sentimentChart").getContext("2d");

  new Chart(ctx, {
    type: "pie",
    data: {
      labels: ["Positive", "Neutral", "Negative"],
      datasets: [
        {
          data: [positive, neutral, negative],
          backgroundColor: ["#4caf50", "#ffc107", "#f44336"],
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        title: {
          display: true,
          text: "Team Feedback Sentiment Distribution"
        }
      }
    }
  });
});
