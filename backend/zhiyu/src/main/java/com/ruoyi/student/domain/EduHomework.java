package com.ruoyi.student.domain;

import java.util.Date;
import com.ruoyi.common.core.domain.BaseEntity;

public class EduHomework extends BaseEntity {
    private Long homeworkId;
    private String title;
    private String content;
    private String className;
    private Long teacherId;
    private String teacherName;
    private Date dueTime;
    private String status;

    public Long getHomeworkId() { return homeworkId; }
    public void setHomeworkId(Long homeworkId) { this.homeworkId = homeworkId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }
    public Long getTeacherId() { return teacherId; }
    public void setTeacherId(Long teacherId) { this.teacherId = teacherId; }
    public String getTeacherName() { return teacherName; }
    public void setTeacherName(String teacherName) { this.teacherName = teacherName; }
    public Date getDueTime() { return dueTime; }
    public void setDueTime(Date dueTime) { this.dueTime = dueTime; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
