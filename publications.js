const publications = [
  {
    id: "curbscan",
    title: "CurbScan: Curb Detection and Tracking Using Multi-Sensor Fusion",
    authors: ["Iljoo Baek", "Tzu-Chieh Tai", "Manoj Mohan Bhat", "Karun Ellango", "Tarang Shah", "Kamal Fuseini", "Ragunathan (Raj) Rajkumar"],
    conference: "arXiv",
    year: 2020,
    links: ["https://www.youtube.com/watch?v=w5MwsdWhcy4", "https://www.youtube.com/watch?v=Gd506RklfG8"],
    description: "CurbScan introduces an approach for curb detection and tracking in urban environments by fusing data from sparse LiDAR, a mono camera, and ultrasonic sensors. It enhances detection accuracy by removing false positives and boosts tracking with a Kalman filter. The method shows over 90% accuracy in various environments and demonstrates the feasibility of integrating low-cost sensors for enhanced curb detection.",
    imageBefore: "images/curb.png", // Image URLs not provided in the summary
    imageAfter: "images/curb2.png", // Image URLs not provided in the summary
}, 
{
  id: "adas_svop_tltw",
  title: "Advanced Driver Assistance Strategies for a Single-Vehicle Overtaking a Platoon on the Two-Lane Two-Way Road",
  authors: ["Junjie Chen", "Manoj Bhat", "Shiyan Jiang", "Ding Zhao"],
  conference: "IEEE Access",
  year: 2020,
  links: ["https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9072403"],
  description: "This paper presents a framework for Advanced Driver Assistance Strategies (ADAS) tailored for single-vehicle overtaking a platoon on two-lane two-way (TLTW) roads. It introduces a novel algorithm to generate coarse ADAS, utilizing simulations for raw data on driver behavior analysis. A Bayesian nonparametric approach segments driver's overtaking behavior for effective ADAS information filtering, emphasizing vehicle safety, traffic efficiency, and driving comfort.",
  imageBefore: "images/navigate.png", // Image URLs not provided in the summary
  imageAfter: "images/navigate2.png", // Image URLs not provided in the summary
},
{
  id: "density_adaptive_sampling",
  title: "Density-adaptive Sampling for Heterogeneous Point Cloud Object Segmentation in Autonomous Vehicle Applications",
  authors: ["Hasan Asy’ari Arief", "Mansur Maturidi Arief", "Manoj Bhat", "Ulf Geir Indahl", "Håvard Tveite", "Ding Zhao"],
  conference: "Not specified in the document",
  year: "Not specified in the document",
  links: ["https://openaccess.thecvf.com/content_CVPRW_2019/papers/UG2+%20Prize%20Challenge/Arief_Density-Adaptive_Sampling_for_Heterogeneous_Point_Cloud_Object_Segmentation_in_Autonomous_CVPRW_2019_paper.pdf"],
  description: "This paper introduces a density-adaptive sampling method to address the challenge of heterogeneous density distribution in point cloud data for autonomous vehicles. It aims to improve classification accuracy for point clouds with imbalanced class representation. The method balances point density using oversampling and empirically samples from the balanced grid. Experiments on the KITTI Vision 3D Benchmark dataset with PointCNN as the classifier showed a substantial increase in per-class accuracy from 82.73% to 92.25% compared to traditional voxel-based sampling.",
  imageBefore: "images/density.png", // Image URLs not provided in the summary
  imageAfter: "images/density2.png", // Image URLs not provided in the summary
}, 
{
  id: "datf_multimodal",
  title: "Diverse and Admissible Trajectory Forecasting through Multimodal Context Understanding",
  authors: ["Seong Hyeon Park", "Gyubok Lee", "Manoj Bhat", "Jimin Seo", "Minseok Kang", "Jonathan Francis", "Ashwin Jadhav", "Paul Pu Liang", "Louis-Philippe Morency"],
  conference: "arXiv",
  year: 2020,
  links: ["https://github.com/kami93/CMU-DATF"],
  description: "This paper addresses multi-agent trajectory forecasting in autonomous driving by anticipating the behaviors of surrounding vehicles and pedestrians. The proposed model synthesizes multiple input signals from the multimodal world, including the environment’s scene context and interactions between multiple surrounding agents, to model all diverse and admissible trajectories. The paper introduces new metrics for evaluating the diversity of predictions and demonstrates significant performance improvements over previous methods.",
  imageBefore: "images/datf_multimodal.png", // Image URLs not provided in the summary
  imageAfter: "images/datf_multimodal2.png", // Image URLs not provided in the summary
}, 
{
  id: "fast_polar_attentive",
  title: "Fast Polar Attentive 3D Object Detection on LiDAR Point Clouds",
  authors: ["Manoj Bhat", "Steve Han", "Fatih Porikli"],
  conference: "NeurIPS",
  year: 2021,
  links: ["https://www.porikli.com/mysite/pdfs/porikli%202021%20-%20Fast%20polar%20attentive%203D%20object%20detection%20on%20LiDAR%20point%20clouds.pdf"],
  description: "This paper introduces a novel streaming detector for 3D object detection using LiDAR point clouds. The method utilizes polar space feature representations for faster inference and maintains high accuracy, particularly for detecting objects in long ranges. It incorporates pseudo-image features, is efficient for edge devices with limited memory, and outperforms state-of-the-art methods in the KITTI and Waymo datasets. The approach is crucial for applications like autonomous driving and map building, emphasizing reduced computational load and latency.",
  imageBefore: "images/polar.png", // Image URLs not provided in the summary
  imageAfter: "images/polar2.png", // Image URLs not provided in the summary
}, 
{
  id: "intelligent_navigation",
  title: "Intelligent Navigation for Autonomous Vehicles in Urban Environments",
  authors: ["JunJie Chen", "Wei ShangGuan", "Baigen Cai", "Manoj Bhat", "Yu Du"],
  conference: "IEEE",
  year: 2020,
  links: ["https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9072403"],
  description: "The platoon makes the ego vehicle face the problem of overtaking, which not only interfering with the traffic efficiency improving but also adding the risk of collision. In order to solve this problem, a step-by-step VOPDS (vehicle overtakes the platoon based on driving style) algorithm was proposed, in which an optimal speed matching scheme by researching the relationship between the speed of vehicles before the slot, the speed of vehicles behind the slot, the speed of vehicle joining a platoon and the required safety slot was designed. ",
  imageBefore: "images/platoon.png", // Image URLs not provided in the summary
  imageAfter: "images/platoon2.png", // Image URLs not provided in the summary
}, {
  id: "sane",
  title: "Smart Annotation and Evaluation Tools for Point Cloud Data",
  authors: ["Hasan Asy’ari Arief", "Mansur Arief", "Guilin Zhang", "Zuxin Liu", "Manoj Bhat", "Ulf Geir Indahl", "Håvard Tveite", "Ding Zhao"],
  conference: "IEEE Access",
  year: 2020,
  links: ["https://ieeexplore.ieee.org/document/9081590"], // Example link, actual links not provided in the summary
  description: "SAnE is a semiautomatic annotation tool for labeling point cloud data, emphasizing high-quality, time-efficient, and user-friendly annotation. It proposes a novel denoising pointwise segmentation strategy for one-click annotation, expands the motion model technique with a guided-tracking algorithm, and offers an interactive, robust, open-source tool for both skilled and crowdsourcing annotators. The tool significantly improves annotation speed and accuracy, evidenced by experiments using the KITTI dataset.",
  imageBefore: "images/sane.png", // Image URLs not provided in the summary
  imageAfter: "images/sane2.png", // Image URLs not provided in the summary
}, 
{
  id: "trajformer",
  title: "Trajformer: Trajectory Prediction with Local Self-Attentive Contexts for Autonomous Driving",
  authors: ["Manoj Bhat", "Jonathan Francis", "Jean Oh"],
  conference: "NeurIPS",
  year: 2020,
  links: ["https://github.com/Manojbhat09/Trajformer"],
  description: "Trajformer introduces a novel self-attention-based encoding structure for trajectory prediction in autonomous driving. It significantly improves the modeling of social contextual relationships by better characterizing agent behavior and social etiquette, enhancing trajectory prediction accuracy. The model showcases improved parameter efficiency and outperforms various baselines on the Argoverse dataset across standard metrics like minADE and minFDE.",
  imageBefore: "images/trajformer.png", // Image URLs not provided in the summary
  imageAfter: "images/trajformer2.png", // Image URLs not provided in the summary
},
    // ... other publications
];

function renderPublications() {
    const container = document.getElementById('publicationsContainer');
    container.innerHTML = publications.map(publication => publicationTemplate(publication)).join('');
}

function publicationTemplate(publication) {
    return `
      <tr onmouseout="${publication.id}_stop()" onmouseover="${publication.id}_start()">
        <td style="padding:20px;width:25%;vertical-align:middle">
          <div class="one">
            <div class="two" id='${publication.id}_image'>
              <img src='${publication.imageAfter}' width="160">
            </div>
            <img src='${publication.imageBefore}' width="160">
          </div>
        </td>
        <td style="padding:20px;width:75%;vertical-align:middle">
          <a href="${publication.links[0]}">
            <span class="papertitle">${publication.title}</span>
          </a>
          <br>
          ${publication.authors.map(author => `<a href="#">${author}</a>`).join(', ')}
          <br>
          <em>${publication.conference}</em>, ${publication.year}
          <br>
          ${publication.links.map(link => `<a href="${link}">link</a>`).join(' / ')}
          <p>${publication.description}</p>
        </td>
      </tr>
    `;
  }
  

function startStopFunctions(publication) {
    window[`${publication.id}_start`] = function() {
      document.getElementById(`${publication.id}_image`).style.opacity = "1";
    };
    window[`${publication.id}_stop`] = function() {
      document.getElementById(`${publication.id}_image`).style.opacity = "0";
    };
  }



document.addEventListener("DOMContentLoaded", function() {
    publications.forEach(publication => {
        document.getElementById('publicationsContainer').innerHTML += publicationTemplate(publication);
        startStopFunctions(publication);
      });

      renderPublications();
});