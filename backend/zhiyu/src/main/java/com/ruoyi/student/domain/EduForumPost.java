package com.ruoyi.student.domain;

import java.util.Date;

public class EduForumPost
{
    private Long postId;
    private String title;
    private String content;
    private Long authorId;
    private String authorName;
    private String authorRole;
    private String targetRole;
    private String className;
    private Date createTime;

    public Long getPostId()
    {
        return postId;
    }

    public void setPostId(Long postId)
    {
        this.postId = postId;
    }

    public String getTitle()
    {
        return title;
    }

    public void setTitle(String title)
    {
        this.title = title;
    }

    public String getContent()
    {
        return content;
    }

    public void setContent(String content)
    {
        this.content = content;
    }

    public Long getAuthorId()
    {
        return authorId;
    }

    public void setAuthorId(Long authorId)
    {
        this.authorId = authorId;
    }

    public String getAuthorName()
    {
        return authorName;
    }

    public void setAuthorName(String authorName)
    {
        this.authorName = authorName;
    }

    public String getAuthorRole()
    {
        return authorRole;
    }

    public void setAuthorRole(String authorRole)
    {
        this.authorRole = authorRole;
    }

    public String getTargetRole()
    {
        return targetRole;
    }

    public void setTargetRole(String targetRole)
    {
        this.targetRole = targetRole;
    }

    public String getClassName()
    {
        return className;
    }

    public void setClassName(String className)
    {
        this.className = className;
    }

    public Date getCreateTime()
    {
        return createTime;
    }

    public void setCreateTime(Date createTime)
    {
        this.createTime = createTime;
    }
}
