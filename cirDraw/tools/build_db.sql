use flappybird;


CREATE TABLE SubmissionTable (
    id INT,
    md5 VARCHAR(255) NOT NULL,
    submission_time datetime,
    upload_file_location VARCHAR(255),
    youtube_url VARCHAR(255),
    andrewid VARCHAR(255),
    username VARCHAR(255),
    category INT,
    best_score INT,
    train_time FLOAT,
    train_episode INT, 
    train_deaths INT,
    num_nn INT,
    PRIMARY KEY (md5)
);

