-- -------------- Meta user creation ------------
USE mysql;
DELIMITER //

CREATE PROCEDURE EnsureUserExists()
BEGIN
    DECLARE userExists INT;
    SET @username := 'bird_agent';
    SET @password := 'flappy';

    SELECT COUNT(*) INTO userExists FROM mysql.user WHERE user = @username;

    IF userExists = 0 THEN
        SET @sql := CONCAT('CREATE USER ', @username, ' IDENTIFIED BY ''', @password, '''');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        SET @sql := CONCAT('GRANT ALL PRIVILEGES ON *.* TO ', @username, ' WITH GRANT OPTION');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        FLUSH PRIVILEGES;

        SELECT 'meta user created' as META_USER_CREATION_Message;
    ELSE
        SELECT 'meta user existed' as META_USER_CREATION_Message;
    END IF;
END;
//
DELIMITER ;

CALL EnsureUserExists();
DROP PROCEDURE EnsureUserExists;



-- -------------- Database creation ------------

DELIMITER //

CREATE PROCEDURE EnsureDatabaseExists()
BEGIN
    -- Check if the 'flappybird' database exists
    SET @dbname := 'flappybird';
    SET @dbExists := (
        SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = @dbname
    );

    -- Conditionally create the database or report it exists
    IF @dbExists = 0 THEN
        SET @sql := CONCAT('CREATE DATABASE ', @dbname);
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;

        SELECT 'Database created successfully.' AS DATABASE_CREATION_MESSAGE;  -- Inform about database creation
    ELSE
        SELECT 'Database already exists.' AS DATABASE_CREATION_MESSAGE;  -- Inform that no action was taken
    END IF;
END;
//
DELIMITER ;

-- Execute the procedure
CALL EnsureDatabaseExists();
DROP PROCEDURE EnsureDatabaseExists;



use flappybird;


-- CREATE TABLE SubmissionTable (
--     id INT,
--     md5 VARCHAR(255) NOT NULL,
--     submission_time datetime,
--     upload_file_location VARCHAR(255),
--     youtube_url VARCHAR(255),
--     andrewid VARCHAR(255),
--     username VARCHAR(255),
--     category INT,
--     best_score INT,
--     train_time FLOAT,
--     train_episode INT, 
--     train_deaths INT,
--     num_nn INT,
--     PRIMARY KEY (md5)
-- );

