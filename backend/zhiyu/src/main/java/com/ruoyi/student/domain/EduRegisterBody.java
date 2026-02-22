package com.ruoyi.student.domain;

/**
 * Pad 端注册请求体
 */
public class EduRegisterBody
{
    private String username;
    private String password;
    private String code;
    private String uuid;
    private String roleKey;
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

    public String getCode()
    {
        return code;
    }

    public void setCode(String code)
    {
        this.code = code;
    }

    public String getUuid()
    {
        return uuid;
    }

    public void setUuid(String uuid)
    {
        this.uuid = uuid;
    }

    public String getRoleKey()
    {
        return roleKey;
    }

    public void setRoleKey(String roleKey)
    {
        this.roleKey = roleKey;
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
