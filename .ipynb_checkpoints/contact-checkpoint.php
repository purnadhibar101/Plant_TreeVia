<?php
$servername = "localhost";  // Change if needed
$username = "root";         // Your MySQL username
$password = "";             // Your MySQL password
$dbname = "plant_info";     // Your database name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get form data
$name = $_POST['name'];
$email = $_POST['email'];
$message = $_POST['message'];

// SQL Query to insert data
$sql = "INSERT INTO contacts (name, email, message) VALUES ('$name', '$email', '$message')";

if ($conn->query($sql) === TRUE) {
    echo "✅ Message sent successfully!";
} else {
    echo "❌ Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
