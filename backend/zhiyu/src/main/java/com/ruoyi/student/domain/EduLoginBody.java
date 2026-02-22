package com.ruoyi.student.domain;

/**
 * Pad 端登录请求体
 */
public class EduLoginBody
{
    private String username;
    private String password;
    private Integer gradeNo;
    private Integer classNo;

    public String getUsername()
    {
        return username;
    }

    public void setUsername(String username)
    {
        this.username = username;
    }

    public String getPassword()
    {
        return password;
    }

    public void setPassword(String password)
    {
        this.password = password;
    }

    public Integer getGradeNo()
    {
        return gradeNo;
    }

    public void setGradeNo(Integer gradeNo)
    {
        this.gradeNo = gradeNo;
    }

    public Integer getClassNo()
    {
        return classNo;
    }

    public void setClassNo(Integer classNo)
    {
        this.classNo = classNo;
    }
}
