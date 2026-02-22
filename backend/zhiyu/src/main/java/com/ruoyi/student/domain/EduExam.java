package com.ruoyi.student.domain;

import java.util.Date;
import com.ruoyi.common.core.domain.BaseEntity;

public class EduExam extends BaseEntity {
    private Long examId;
    private String title;
    private String className;
    private Long teacherId;
    private String teacherName;
    private Date examTime;
    private Integer totalScore;

    public Long getExamId() { return examId; }
    public void setExamId(Long examId) { this.examId = examId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }
    public Long getTeacherId() { return teacherId; }
    public void setTeacherId(Long teacherId) { this.teacherId = teacherId; }
    public String getTeacherName() { return teacherName; }
    public void setTeacherName(String teacherName) { this.teacherName = teacherName; }
    public Date getExamTime() { return examTime; }
    public void setExamTime(Date examTime) { this.examTime = examTime; }
    public Integer getTotalScore() { return totalScore; }
    public void setTotalScore(Integer totalScore) { this.totalScore = totalScore; }
}
