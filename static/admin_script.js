    let currentEditType = ''; // To track if editing a user or an activity

    // Fetch users from the server
    async function fetchUsers() {
        const response = await fetch('/get_users');
        const users = await response.json();
        const userTableBody = document.getElementById('user-table-body');
        
        userTableBody.innerHTML = ''; // Clear existing rows

        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.email}</td>
                <td>${user.password}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="editUser(${user.id}, '${user.email}', '${user.password}')">Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteUser(${user.id})">Delete</button>
                </td>
            `;
            userTableBody.appendChild(row);
        });
    }

    // Fetch activities from the server
    async function fetchActivities() {
        const response = await fetch('/get_activities');
        const activities = await response.json();
        const activityTableBody = document.getElementById('activity-table-body');
        
        activityTableBody.innerHTML = ''; // Clear existing rows

        activities.forEach(activity => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${activity.id}</td>
                <td>${activity.activityType}</td>
                <td>${activity.duration}</td>
                <td>${activity.calories}</td>
                <td>${activity.date}</td>
                <td>
                    <button class="btn btn-warning btn-sm" onclick="editActivity(${activity.id}, '${activity.activityType}', ${activity.duration}, ${activity.calories}, '${activity.date}')">Edit</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteActivity(${activity.id})">Delete</button>
                </td>
            `;
            activityTableBody.appendChild(row);
        });
    }

    // Edit a user
    function editUser(id, email, password) {
        currentEditType = 'user';
        document.getElementById('edit-id').value = id;
        document.getElementById('edit-email').value = email;
        document.getElementById('edit-password').value = password;
        document.getElementById('edit-user-fields').style.display = 'block';
        document.getElementById('edit-activity-fields').style.display = 'none';
        document.getElementById('edit-form').style.display = 'block';
    }

    // Edit an activity
    function editActivity(id, activityType, duration, calories, date) {
        currentEditType = 'activity';
        document.getElementById('edit-id').value = id;
        document.getElementById('edit-activityType').value = activityType;
        document.getElementById('edit-duration').value = duration;
        document.getElementById('edit-calories').value = calories;
        document.getElementById('edit-date').value = date;
        document.getElementById('edit-user-fields').style.display = 'none';
        document.getElementById('edit-activity-fields').style.display = 'block';
        document.getElementById('edit-form').style.display = 'block';
    }

    // Save changes
    document.getElementById('save-changes').addEventListener('click', async () => {
        const id = document.getElementById('edit-id').value;
        
        if (currentEditType === 'user') {
            const email = document.getElementById('edit-email').value;
            const password = document.getElementById('edit-password').value;
            await fetch(`/update_user/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
            fetchUsers(); // Refresh the user list
        } else if (currentEditType === 'activity') {
            const activityType = document.getElementById('edit-activityType').value;
            const duration = document.getElementById('edit-duration').value;
            const calories = document.getElementById('edit-calories').value;
            const date = document.getElementById('edit-date').value;
            await fetch(`/update_activity/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ activityType, duration, calories, date }),
            });
            fetchActivities(); // Refresh the activity list
        }
        document.getElementById('edit-form').style.display = 'none'; // Hide the edit form
    });

    // Delete a user
    async function deleteUser(userId) {
        const response = await fetch(`/delete_user/${userId}`, {
            method: 'DELETE',
        });
        const result = await response.json();
        alert(result.message);
        fetchUsers(); // Refresh the user list
    }

    // Delete an activity
    async function deleteActivity(activityId) {
        const response = await fetch(`/delete_activity/${activityId}`, {
            method: 'DELETE',
        });
        const result = await response.json();
        alert(result.message);
        fetchActivities(); // Refresh the activity list
    }

    // Initialize the dashboard
    document.addEventListener('DOMContentLoaded', () => {
        fetchUsers();
        fetchActivities();
    });

// Create header section
    const header = document.createElement('div');
    header.className = 'd-flex justify-content-between align-items-center mb-3';

    // Create title
    const title = document.createElement('h1');
    title.className = 'text-center flex-grow-1';
    title.textContent = '⚙️ Admin Dashboard';

    // Create logout button with Font Awesome icon
const logoutBtn = document.createElement('button');
logoutBtn.id = 'logoutBtn';
logoutBtn.className = 'btn btn-danger logout-btn d-flex align-items-center';

// Set inner HTML with icon
logoutBtn.innerHTML = '<i class="fa-solid fa-right-from-bracket"></i> Logout';

// Optional styling via JS
logoutBtn.style.display = 'flex';
logoutBtn.style.alignItems = 'center';
logoutBtn.style.gap = '6px';

// Append to header
header.appendChild(logoutBtn);


    // Append title and button to header
    header.appendChild(title);
    header.appendChild(logoutBtn);

    // Append header to app div
    document.getElementById('app').appendChild(header);

    // Add event listener to logout button

