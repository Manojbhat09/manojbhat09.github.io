const workExperiences = [
    {
      company: "Rivian",
      logo: "images/rivian_logo.png",
      role: "Machine Learning Engineer II",
      department: "Offboard Planning, Planning & Simulation",
      duration: "Apr/2’23 – Present",
      achievements: [
        "Spearheaded the implementation of Wayformer, a state-of-the-art motion forecasting model.",
        "Contributed to Neural Rendering Fields and published a patent with Rivian.",
        "Optimized model training procedures using Ray.io."
      ]
    },
    {
      company: "Amazon Robotics",
      logo: "images/amazon_robotics_logo.png",
      role: "Machine Learning Engineer II",
      department: "Scout, Perception & Simulation",
      duration: "Oct/2’21 – Feb/2’23",
      achievements: [
        "Lead AWS distributed system design for scaling ML models.",
        "Enhanced simulation realism for autonomy scaling.",
        "Improved trajectory prediction with unsupervised learning."
      ]
    },

    {
        company: "Qualcomm",
        logo: "images/qualcomm_logo.png",
        role: "Research Software Engineer",
        department: "3D LiDAR Detection, Behavior Planning & Deep Learning",
        duration: "Sept/2’20 – Oct/2’21",
        achievements: [
          "Implemented Lane Graphs & VectorNet for improved vehicle behavior prediction.",
          "Developed a Sequence based Streaming LiDAR 3D Transformer Object detection ML pipeline.",
          "Conducted research on self-supervised methods for Domain Adaptation."
        ]
      },
      {
        company: "Bosch",
        logo: "images/bosch_logo.png",
        role: "Software Engineer, Computer Vision",
        department: "",
        duration: "May/2’19 – Sept/2’19",
        achievements: [
          "Developed algorithms for image processing and computer vision.",
          "Optimized object detection algorithms for improved accuracy."
        ]
      },
      {
        company: "Carnegie Mellon University",
        logo: "images/cmu_logo.png",
        role: "Research Assistant",
        department: "",
        duration: "Date Started – May/2’20",
        achievements: [
          "Engaged in research and development in robotics and computer vision.",
          "Contributed to several high-impact academic research projects."
        ]
      },
    // ... other experiences
  ];
  

  function renderWorkExperiences() {
    const container = document.getElementById('workExperienceContainer');
    container.innerHTML = workExperiences.map(exp => {
      return `
        <tr>
          <td style="padding: 5px;width:25%;vertical-align:middle">
            <img src="${exp.logo}" alt="${exp.company} Logo" class="company-logo">
          </td>
          <td style="padding:20px;width:75%;vertical-align:middle">
            <h3>${exp.role}</h3>
            <h4>${exp.company}</h4>
            <p>${exp.duration}</p>
            <ul>
              ${exp.achievements.map(achievement => `<li>${achievement}</li>`).join('')}
            </ul>
          </td>
        </tr>
      `;
    }).join('');
  }
  
  document.addEventListener("DOMContentLoaded", function() {
    renderWorkExperiences();
  });