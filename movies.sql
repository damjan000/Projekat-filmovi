-- Create the database
CREATE DATABASE movies;

-- Select the database
USE movies;

-- Create the "Movies" table
CREATE TABLE Movies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  duration INT,
  genre VARCHAR(255),
  rating DECIMAL(5,1),
  description TEXT,
  image_url VARCHAR(255)
);

-- Create the "Actors" table
CREATE TABLE Actors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL
);

-- Create the "Movie_Actor" table to link movies and actors
CREATE TABLE Movie_Actor (
  id INT AUTO_INCREMENT PRIMARY KEY,
  movie_id INT,
  actor_id INT,
  FOREIGN KEY (movie_id) REFERENCES Movies(id),
  FOREIGN KEY (actor_id) REFERENCES Actors(id)
);

-- Create the "Users" table to store user information
CREATE TABLE Users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

-- Create the "Reviews" table to store user reviews for movies
CREATE TABLE Reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  movie_id INT,
  user_id INT,
  username VARCHAR(255),
  rating INT,
  comment TEXT,
  FOREIGN KEY (movie_id) REFERENCES Movies(id),
  FOREIGN KEY (user_id) REFERENCES Users(id)
);


