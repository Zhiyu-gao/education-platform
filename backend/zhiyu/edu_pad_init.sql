-- Pad 端作业/考试/任务初始化表

CREATE TABLE IF NOT EXISTS edu_homework (
  homework_id BIGINT NOT NULL AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  class_name VARCHAR(100) DEFAULT NULL,
  teacher_id BIGINT NOT NULL,
  teacher_name VARCHAR(100) DEFAULT NULL,
  due_time DATETIME DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'PUBLISHED',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (homework_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_homework_submission (
  submission_id BIGINT NOT NULL AUTO_INCREMENT,
  homework_id BIGINT NOT NULL,
  student_id BIGINT NOT NULL,
  student_name VARCHAR(100) DEFAULT NULL,
  answer_content TEXT,
  submit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  score INT DEFAULT NULL,
  feedback VARCHAR(500) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (submission_id),
  UNIQUE KEY uk_homework_student (homework_id, student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_exam (
  exam_id BIGINT NOT NULL AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  class_name VARCHAR(100) DEFAULT NULL,
  teacher_id BIGINT NOT NULL,
  teacher_name VARCHAR(100) DEFAULT NULL,
  exam_time DATETIME DEFAULT NULL,
  total_score INT DEFAULT 100,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (exam_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_exam_score (
  score_id BIGINT NOT NULL AUTO_INCREMENT,
  exam_id BIGINT NOT NULL,
  student_id BIGINT NOT NULL,
  student_name VARCHAR(100) DEFAULT NULL,
  score INT DEFAULT NULL,
  remark VARCHAR(500) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (score_id),
  UNIQUE KEY uk_exam_student (exam_id, student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_teacher_task (
  task_id BIGINT NOT NULL AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  teacher_id BIGINT NOT NULL,
  teacher_name VARCHAR(100) DEFAULT NULL,
  due_time DATETIME DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'TODO',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_forum_post (
  post_id BIGINT NOT NULL AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  author_id BIGINT NOT NULL,
  author_name VARCHAR(100) DEFAULT NULL,
  author_role VARCHAR(20) DEFAULT NULL,
  target_role VARCHAR(20) DEFAULT 'ALL',
  class_name VARCHAR(50) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (post_id),
  KEY idx_forum_post_create_time (create_time),
  KEY idx_forum_post_target_role (target_role),
  KEY idx_forum_post_class_name (class_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_forum_reply (
  reply_id BIGINT NOT NULL AUTO_INCREMENT,
  post_id BIGINT NOT NULL,
  content TEXT,
  author_id BIGINT NOT NULL,
  author_name VARCHAR(100) DEFAULT NULL,
  author_role VARCHAR(20) DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (reply_id),
  KEY idx_forum_reply_post_id (post_id),
  KEY idx_forum_reply_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_forum_read_state (
  user_id BIGINT NOT NULL,
  last_read_time DATETIME DEFAULT NULL,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS edu_user_class_profile (
  user_id BIGINT NOT NULL,
  role_key VARCHAR(20) NOT NULL,
  grade_no INT NOT NULL,
  class_no INT NOT NULL,
  class_name VARCHAR(50) NOT NULL,
  head_teacher TINYINT(1) DEFAULT 0,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT NULL,
  PRIMARY KEY (user_id),
  KEY idx_profile_class_name (class_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE student_performance
  ADD COLUMN IF NOT EXISTS grade_no INT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS class_no INT DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS class_name VARCHAR(50) DEFAULT NULL;
