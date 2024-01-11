const updates = [
    {
      date: "2023/09",
      content: "Participated in an Internal Hackathon on Generative AI at Rivian, resulting in a published patent.",
      highlight: false,
      link: 'link-to-update-1'
    },
    {
      date: "2023/06",
      content: "Attended workshops focusing on GPT and deep learning technologies, enriching my expertise in AI.",
      highlight: false,
      link: 'link-to-update-1'
    },
    {
      date: "2023/04",
      content: "Collaborated on optimizing model training procedures, enhancing efficiency and scalability at Rivian.",
      highlight: false,
      link: 'link-to-update-1'
    }

    
    // ... other updates
  ];

  function renderUpdates() {
    const container = document.getElementById('updatesContainer');
    container.innerHTML = '<ul class="news-updates-list">' + updates.map(update => updateTemplate(update)).join('') + '</ul>';  }
  
    function updateTemplate(update) {
      return `
          <div class="news-update ${update.highlight ? 'highlight' : ''}">
              <span class="update-date"><a href="${update.link}">${update.date}</a></span>
              <span class="update-content">${update.content}</span>
          </div>
      `;
  }
  
  document.addEventListener("DOMContentLoaded", function() {
    renderUpdates();
  });