document.addEventListener("DOMContentLoaded", () => {
	// function to fetch the courses from the backend
	const fetchCourses = () => {
		fetch("/get_courses")
			.then((response) => response.json())
			.then((data) => {
				// call arrow function to display the courses
				displayCourses(data.courses);
			})
			.catch((error) => console.error("Error fetching courses: ", error));
	};

	// Function to display courses in the html
	const displayCourses = (courses) => {
		const courseList = document.getElementById("course-list");
		courseList.innerHTML = ""; // clear the current course list

		// Loop through the courses and create the html elements for each
		courses.forEach((course) => {
			const courseElement = document.createElement("div");
			courseElement.classList.add("course");

			// Add course details
			courseElement.innerHTML = `
                <h2>${course[1]}</h2>  <!-- course[1]: Name -->
                <p>Location: ${course[2]}</p>  <!-- course[2]: Address -->
                <p>Phone: ${course[3]}</p>  <!-- course[3]: Phone -->
                <p>Holes: ${course[4]}</p>  <!-- course[4]: Holes -->
                <p>Par: ${course[5]}</p>  <!-- course[5]: Par for the course -->
                <p>Front Nine Par: ${course[6]}</p>  <!-- course[6]: Par for the front nine -->
                <p>Back Nine Par: ${course[7]}</p>  <!-- course[7]: Par for the back nine -->
            
            `;

			// Append the course element to the course list
			courseList.appendChild(courseElement);
		});
	};

	// Fetch the courses when the page loads
	fetchCourses();
});
