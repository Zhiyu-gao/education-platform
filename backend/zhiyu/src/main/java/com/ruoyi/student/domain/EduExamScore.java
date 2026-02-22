package com.ruoyi.student.domain;

import com.ruoyi.common.core.domain.BaseEntity;

public class EduExamScore extends BaseEntity {
    private Long scoreId;
    private Long examId;
    private Long studentId;
    private String studentName;
    private Integer score;
    private String remark;

    public Long getScoreId() { return scoreId; }
    public void setScoreId(Long scoreId) { this.scoreId = scoreId; }
    public Long getExamId() { return examId; }
    public void setExamId(Long examId) { this.examId = examId; }
    public Long getStudentId() { return studentId; }
    public void setStudentId(Long studentId) { this.studentId = studentId; }
    public String getStudentName() { return studentName; }
    public void setStudentName(String studentName) { this.studentName = studentName; }
    public Integer getScore() { return score; }
    public void setScore(Integer score) { this.score = score; }
    public String getRemark() { return remark; }
    public void setRemark(String remark) { this.remark = remark; }
}
